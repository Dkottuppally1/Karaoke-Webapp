"""
Karaoke Webapp Backend
Main FastAPI application for audio source separation
"""

import os
import ssl
import shutil
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
import tempfile
import time

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

# Fix SSL certificate issues on macOS
import certifi
import ssl as ssl_lib

# Set default SSL context to use certifi certificates
try:
    # Try to use certifi certificates
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    ssl_lib._create_default_https_context = lambda: ssl_context
except Exception:
    # Fallback: for macOS, sometimes we need to install certificates
    # This is a workaround - in production, ensure proper certificates are installed
    import urllib.request
    import urllib.error
    
    # Try to install certificates (macOS specific)
    try:
        import subprocess
        subprocess.run(['/Applications/Python*/Install Certificates.command'], shell=True, check=False)
    except:
        pass
    
    # Use certifi as fallback
    ssl_lib._create_default_https_context = lambda: ssl_lib.create_default_context(cafile=certifi.where())

from separation_engine import separate_audio, setup_model

# Output directory for generated files
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Clean up old files (older than 1 hour)
CLEANUP_AGE_SECONDS = 3600

# Global model instance (loaded once at startup)
model = None

def cleanup_old_files():
    """Remove files older than CLEANUP_AGE_SECONDS"""
    current_time = time.time()
    for file_path in OUTPUT_DIR.glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > CLEANUP_AGE_SECONDS:
                file_path.unlink()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    global model
    print("Loading source separation model...")
    try:
        model = setup_model()
        cleanup_old_files()
        print("Model loaded and ready!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Server will start but separation will not work until model is loaded.")
        model = None
    
    yield
    
    # Shutdown (cleanup if needed)
    print("Shutting down...")

app = FastAPI(title="Karaoke Generator API", lifespan=lifespan)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Karaoke Generator API is running", "status": "ready"}

@app.get("/api/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "message": "API is ready" if model else "API is ready but model not loaded"
    }

@app.post("/api/separate")
async def separate_endpoint(file: UploadFile = File(...)):
    """
    Main endpoint: takes an audio file and returns separated stems
    
    Returns:
        - instrumental: karaoke track (music only)
        - vocals: isolated vocal track
        - original: original file (for comparison)
    """
    # Validate file type
    allowed_extensions = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary directory for input processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Save uploaded file
        input_path = temp_path / f"input{file_ext}"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Check file size (limit to ~50MB)
        file_size = input_path.stat().st_size
        if file_size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size: 50MB"
            )
        
        try:
            # Run separation (outputs to persistent OUTPUT_DIR)
            result = separate_audio(
                model=model,
                input_path=str(input_path),
                output_dir=str(OUTPUT_DIR)
            )
            
            # Clean up old files periodically
            cleanup_old_files()
            
            # Return file paths
            return JSONResponse({
                "status": "success",
                "message": "Audio separated successfully",
                "files": {
                    "instrumental": f"/api/download/{result['instrumental_id']}",
                    "vocals": f"/api/download/{result['vocals_id']}",
                    "original": f"/api/download/{result['original_id']}"
                },
                "metadata": result.get("metadata", {})
            })
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Separation failed: {str(e)}"
            )

@app.get("/api/download/{file_id}")
async def download_file(file_id: str):
    """
    Download endpoint for generated files
    Serves files from the OUTPUT_DIR
    """
    file_path = OUTPUT_DIR / file_id
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    media_type = "audio/wav" if file_id.endswith(".wav") else "application/octet-stream"
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=file_id
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

