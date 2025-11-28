"""
Audio Source Separation Engine
Core logic for splitting audio into vocals and instrumental
"""

import os
import uuid
from pathlib import Path
from typing import Dict, Optional
import numpy as np
import torch
import torchaudio
from demucs.pretrained import get_model
from demucs.audio import AudioFile, convert_audio
from demucs.apply import apply_model
import soundfile as sf
import librosa

# Global model cache
_model_cache = None

def ensure_numpy(data):
    """
    Helper function to ensure data is a numpy array.
    Converts PyTorch tensors to numpy arrays.
    
    Args:
        data: Can be torch.Tensor, np.ndarray, or other array-like
    
    Returns:
        numpy.ndarray
    """
    if isinstance(data, torch.Tensor):
        return data.cpu().detach().numpy()
    elif isinstance(data, np.ndarray):
        return data
    else:
        return np.array(data)

def setup_model(model_name: str = "htdemucs") -> torch.nn.Module:
    """
    Load and cache the separation model
    
    Args:
        model_name: Demucs model variant (htdemucs is good quality/speed balance)
    
    Returns:
        Loaded model ready for inference
    """
    global _model_cache
    
    if _model_cache is None:
        print(f"Loading {model_name} model...")
        _model_cache = get_model(model_name)
        _model_cache.eval()  # Set to evaluation mode
        print("Model loaded successfully!")
    
    return _model_cache

def normalize_audio(audio: np.ndarray, target_db: float = -23.0) -> np.ndarray:
    """
    Normalize audio to a target loudness level
    
    Args:
        audio: Audio array (can be 1D or 2D [samples, channels])
        target_db: Target loudness in dB
    
    Returns:
        Normalized audio array
    """
    # Ensure input is numpy array (soundfile, librosa, etc. all need numpy)
    audio = ensure_numpy(audio)
    
    if audio.size == 0:
        return audio
    
    # Handle multi-channel audio
    if audio.ndim == 2:
        # Calculate RMS per channel, then average
        rms = np.sqrt(np.mean(audio**2, axis=0))
        rms = np.mean(rms)  # Average across channels
    else:
        # Mono audio
        rms = np.sqrt(np.mean(audio**2))
    
    if rms == 0:
        return audio
    
    # Calculate current level in dB
    current_db = 20 * np.log10(rms + 1e-10)  # Add small epsilon to avoid log(0)
    
    # Calculate gain needed
    gain_db = target_db - current_db
    gain_linear = 10 ** (gain_db / 20)
    
    # Apply gain (with safety limit)
    normalized = audio * min(gain_linear, 10.0)  # Max 10x gain
    
    # Prevent clipping
    max_val = np.max(np.abs(normalized))
    if max_val > 1.0:
        normalized = normalized / max_val * 0.95
    
    return normalized

def apply_fade(audio: np.ndarray, sample_rate: int, fade_ms: int = 50) -> np.ndarray:
    """
    Apply fade-in and fade-out to prevent clicks
    
    Args:
        audio: Audio array, shape [samples] or [samples, channels]
        sample_rate: Sample rate
        fade_ms: Fade duration in milliseconds
    
    Returns:
        Audio with fades applied
    """
    # Ensure input is numpy array
    audio = ensure_numpy(audio)
    
    fade_samples = int(sample_rate * fade_ms / 1000)
    
    # Not enough samples for both fades → skip
    if audio.shape[0] < fade_samples * 2:
        return audio
    
    # 1D mono: shape (N,)
    if audio.ndim == 1:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        audio = audio.copy()
        audio[:fade_samples] *= fade_in
        audio[-fade_samples:] *= fade_out
    
    # 2D stereo: [samples, channels]
    elif audio.ndim == 2:
        # Reshape fades to (fade_samples, 1) for proper broadcasting
        fade_in = np.linspace(0, 1, fade_samples)[:, None]   # (fade_samples, 1)
        fade_out = np.linspace(1, 0, fade_samples)[:, None]  # (fade_samples, 1)
        
        audio = audio.copy()
        # Broadcast: (fade_samples, channels) * (fade_samples, 1) → (fade_samples, channels)
        audio[:fade_samples, :] *= fade_in
        audio[-fade_samples:, :] *= fade_out
    
    else:
        # Unexpected shape; just return unchanged
        return audio
    
    return audio

def apply_vocal_eq(audio: np.ndarray, sample_rate: int, cut_db: float = -3.0) -> np.ndarray:
    """
    Light EQ cut around vocal frequencies (1-4 kHz) to reduce vocal residue
    
    Args:
        audio: Audio array
        sample_rate: Sample rate
        cut_db: Cut amount in dB (negative value)
    
    Returns:
        EQ'd audio
    """
    # Ensure input is numpy array (scipy.signal needs numpy)
    audio = ensure_numpy(audio)
    
    # Simple IIR filter for vocal range
    # This is a simplified approach - in production you'd use proper EQ
    try:
        from scipy import signal
        
        # Design a band-stop filter around 1-4 kHz
        nyquist = sample_rate / 2
        low = 1000 / nyquist
        high = 4000 / nyquist
        
        # Butterworth band-stop filter
        b, a = signal.butter(4, [low, high], btype='bandstop')
        filtered = signal.filtfilt(b, a, audio)
        
        # Mix original and filtered (to control cut amount)
        mix = 10 ** (cut_db / 20)
        result = audio * (1 - mix) + filtered * mix
        
        return result
    except ImportError:
        # If scipy not available, skip EQ
        return audio

def separate_audio(
    model: torch.nn.Module,
    input_path: str,
    output_dir: str,
    stems: int = 4,
    remix_mode: str = "instrumental"
) -> Dict:
    """
    Main separation function
    
    Args:
        model: Loaded Demucs model
        input_path: Path to input audio file
        output_dir: Directory to save outputs
        stems: Number of stems (2 or 4)
        remix_mode: "instrumental" (vocals removed) or "vocals_only"
    
    Returns:
        Dictionary with file paths and metadata
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate unique IDs for this separation
    separation_id = str(uuid.uuid4())[:8]
    
    print(f"Output directory: {output_dir}")
    
    # Load audio file
    print(f"Loading audio: {input_path}")
    wav = AudioFile(input_path).read(
        streams=0,
        samplerate=model.samplerate,
        channels=model.audio_channels
    )
    
    # AudioFile.read() already returns a torch.Tensor with shape [channels, samples]
    # So we use it directly - no need for torch.from_numpy()
    audio = wav
    
    # Convert to model's expected format (still a tensor)
    audio = convert_audio(audio, model.samplerate, model.samplerate, model.audio_channels)
    
    # Log audio info
    print(f"Loaded audio tensor shape: {audio.shape}")
    print(f"Sample rate: {model.samplerate}")
    duration_s = audio.shape[-1] / model.samplerate
    print(f"Duration (s): {duration_s:.2f}")
    
    # 🚧 DEV MODE: Set to True to limit processing for faster testing
    # Set to False to process full songs (may take several minutes on CPU)
    DEV_LIMIT = False  # Change to True when debugging
    
    if DEV_LIMIT:
        max_duration_s = 60  # Process only first 60 seconds in dev mode
        max_samples = int(max_duration_s * model.samplerate)
        
        if audio.shape[-1] > max_samples:
            print(f"⚠️  DEV MODE: Cropping audio to first {max_duration_s} seconds for faster testing.")
            audio = audio[..., :max_samples]
            print(f"New duration: {audio.shape[-1] / model.samplerate:.2f}s")
    else:
        print(f"✅ Processing full song ({duration_s:.2f}s) - this may take a few minutes on CPU...")
    
    # Run separation
    print("Running source separation...")
    
    # Explicitly use CPU for now (can switch to GPU later if available)
    device = torch.device("cpu")
    model.to(device)
    mix = audio.to(device)
    print(f"Running on device: {device}")
    
    with torch.no_grad():
        # apply_model with split=True: required for audio longer than training segment (~7-8s)
        # Demucs will automatically chunk the audio, process each chunk, and cross-fade them
        sources = apply_model(
            model,
            mix[None, ...],     # [1, C, T] - add batch dimension
            split=True,         # ✅ Enable chunking into segments (required for long audio)
            overlap=0.25,       # 25% overlap between chunks (good default for quality)
            shifts=0,           # 0 = no shift-augmentation (faster, simpler for CPU)
            progress=False,     # Disable progress bar for cleaner logs
            device=device,      # Explicitly pass device
        )
        # Remove batch dimension → [sources, channels, samples]
        sources = sources[0].cpu()
        print(f"Separation finished, got sources with shape: {sources.shape}")
    
    # Demucs returns: [drums, bass, other, vocals] for 4-stem models
    # For 2-stem models, check model.sources
    if hasattr(model, 'sources'):
        source_names = model.sources
    else:
        # Default for htdemucs
        source_names = ['drums', 'bass', 'other', 'vocals']
    
    # Extract stems and ensure they're numpy arrays
    stems_dict = {}
    for i, name in enumerate(source_names[:len(sources)]):
        stem_audio = sources[i]
        # Convert to numpy array using helper function
        stem_audio = ensure_numpy(stem_audio)
        stems_dict[name] = stem_audio
    
    # Create instrumental (all except vocals)
    if 'vocals' in stems_dict:
        vocals = ensure_numpy(stems_dict['vocals'])
        
        instrumental_parts = []
        for k in stems_dict.keys():
            if k != 'vocals':
                part = ensure_numpy(stems_dict[k])
                instrumental_parts.append(part)
        
        # Mix instrumental parts
        if len(instrumental_parts) > 1:
            # Sum all instrumental parts
            instrumental = np.sum(instrumental_parts, axis=0)
        else:
            instrumental = instrumental_parts[0] if instrumental_parts else np.zeros_like(vocals)
        
        # Final safety check
        instrumental = ensure_numpy(instrumental)
    else:
        # Fallback if vocals not found
        raise ValueError("Could not extract vocals from model output")
    
    # Post-processing for instrumental
    print("Post-processing instrumental track...")
    
    # Ensure instrumental is numpy array before transpose
    instrumental = ensure_numpy(instrumental)
    instrumental = instrumental.T  # Demucs outputs [channels, samples], we need [samples, channels]
    
    # Normalize
    if instrumental.ndim == 2:
        # Stereo
        instrumental = normalize_audio(instrumental, target_db=-23.0)
    else:
        instrumental = normalize_audio(instrumental, target_db=-23.0)
    
    # Apply fade
    instrumental = apply_fade(instrumental, model.samplerate, fade_ms=50)
    
    # Light EQ to reduce vocal residue
    if instrumental.ndim == 2:
        instrumental[:, 0] = apply_vocal_eq(instrumental[:, 0], model.samplerate, cut_db=-2.0)
        if instrumental.shape[1] > 1:
            instrumental[:, 1] = apply_vocal_eq(instrumental[:, 1], model.samplerate, cut_db=-2.0)
    else:
        instrumental = apply_vocal_eq(instrumental, model.samplerate, cut_db=-2.0)
    
    # Post-processing for vocals
    print("Post-processing vocal track...")
    
    # Ensure vocals is numpy array before transpose
    vocals = ensure_numpy(vocals)
    vocals = vocals.T if vocals.ndim > 1 else vocals
    
    if vocals.ndim == 2:
        vocals = normalize_audio(vocals, target_db=-20.0)  # Slightly quieter
    else:
        vocals = normalize_audio(vocals, target_db=-20.0)
    
    vocals = apply_fade(vocals, model.samplerate, fade_ms=50)
    
    # Save files
    instrumental_path = output_path / f"instrumental_{separation_id}.wav"
    vocals_path = output_path / f"vocals_{separation_id}.wav"
    original_path = output_path / f"original_{separation_id}.wav"
    
    # Final safety check before saving (soundfile requires numpy arrays)
    instrumental = ensure_numpy(instrumental)
    vocals = ensure_numpy(vocals)
    
    # Save as WAV files
    sf.write(str(instrumental_path), instrumental, model.samplerate)
    sf.write(str(vocals_path), vocals, model.samplerate)
    
    # Also save original for comparison
    original_audio = ensure_numpy(audio[0])
    
    # Transpose if needed (handle shape [channels, samples] -> [samples, channels])
    if original_audio.ndim > 1 and original_audio.shape[0] < original_audio.shape[1]:
        original_audio = original_audio.T
    
    sf.write(str(original_path), original_audio, model.samplerate)
    
    print(f"Separation complete! Files saved:")
    print(f"  - {instrumental_path}")
    print(f"  - {vocals_path}")
    print(f"  - {original_path}")
    
    # Get metadata
    duration = len(instrumental) / model.samplerate
    
    return {
        "instrumental_id": f"instrumental_{separation_id}.wav",
        "vocals_id": f"vocals_{separation_id}.wav",
        "original_id": f"original_{separation_id}.wav",
        "metadata": {
            "duration_seconds": round(duration, 2),
            "sample_rate": model.samplerate,
            "channels": instrumental.shape[1] if instrumental.ndim > 1 else 1
        }
    }

