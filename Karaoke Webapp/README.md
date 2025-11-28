# 🎤 Karaoke Generator - AI-Powered Source Separation

A web application that uses AI source separation to create clean karaoke tracks from any song. Upload a song, and get back an instrumental track (music only) and isolated vocals.

## 🎯 What It Does

1. **User uploads** an audio file (MP3, WAV, FLAC, etc.)
2. **Backend processes** the file using Demucs (state-of-the-art source separation)
3. **Returns** three tracks:
   - 🎵 **Karaoke Track** (instrumental, vocals removed)
   - 🎤 **Isolated Vocals** (vocals only)
   - 🔊 **Original Song** (for comparison)

## 🏗️ Architecture

- **Frontend**: React + Vite (modern, fast UI)
- **Backend**: Python + FastAPI (REST API)
- **AI Model**: Demucs (high-quality source separation)
- **Audio Processing**: Post-processing with normalization, EQ, and fades

## 📋 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **~2GB free disk space** (for model downloads)

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The backend will:
- Download the Demucs model on first run (~1.5GB)
- Start on `http://localhost:8000`
- Load the model into memory (takes ~30 seconds)

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Use the App

1. Open `http://localhost:3000` in your browser
2. Click to upload a song (MP3, WAV, FLAC, etc.)
3. Click "Generate Karaoke"
4. Wait for processing (30 seconds - 2 minutes depending on song length)
5. Play and download your separated tracks!

## 📁 Project Structure

```
Karaoke Webapp/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── separation_engine.py  # Core separation logic
│   ├── requirements.txt       # Python dependencies
│   └── outputs/               # Generated files (created automatically)
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── App.css            # Styles
│   │   ├── main.jsx           # React entry point
│   │   └── index.css          # Global styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🎨 Features

### Quality Improvements

The app includes several post-processing steps for better results:

- **Normalization**: Consistent volume levels across tracks
- **EQ Filtering**: Light cut around vocal frequencies (1-4 kHz) to reduce vocal residue in instrumental
- **Fade In/Out**: Prevents clicks and artifacts at track edges
- **Format Consistency**: All outputs are 44.1 kHz WAV files

### User Experience

- **File Validation**: Checks file type and size before processing
- **Progress Indicators**: Shows status during processing
- **Error Handling**: Clear error messages for common issues
- **Audio Players**: Built-in players for all three tracks
- **Download Links**: Easy download for each track

## 🔧 Configuration

### Backend Settings

Edit `backend/app.py` to customize:

- **File size limit**: Currently 50MB (line 77)
- **CORS origins**: Add your frontend URL if different (line 24)
- **Cleanup age**: How long to keep generated files (line 20)

### Model Selection

Edit `backend/separation_engine.py` to change the model:

```python
# In setup_model(), change model_name:
model = get_model("htdemucs")  # Good balance (default)
# model = get_model("htdemucs_ft")  # Fine-tuned, better quality
# model = get_model("mdx_extra")  # Different architecture
```

## 🐛 Troubleshooting

### Model Download Fails

If the model download fails:
- Check your internet connection
- The model is ~1.5GB, so it may take time
- Models are cached in `~/.cache/torch/hub/`

### "CUDA out of memory" Error

If you have a GPU but run out of memory:
- The model will automatically use CPU if GPU memory is insufficient
- For very long songs, consider processing in chunks

### Frontend Can't Connect to Backend

- Make sure backend is running on port 8000
- Check CORS settings in `backend/app.py`
- Verify the proxy in `frontend/vite.config.js`

### Poor Separation Quality

- **Use high-quality input**: Prefer WAV/FLAC or high-bitrate MP3 (320 kbps)
- **Avoid heavily compressed files**: YouTube rips often have artifacts
- **Try different songs**: Some genres (acoustic, simple mixes) separate better than others

## 📚 How It Works (Technical Deep Dive)

### Source Separation Pipeline

1. **Audio Loading**: Converts input to model's expected format (44.1 kHz, stereo)
2. **Model Inference**: Demucs neural network predicts source masks
3. **Stem Extraction**: Separates into drums, bass, other, vocals
4. **Remixing**: Combines drums + bass + other → instrumental
5. **Post-Processing**: Normalization, EQ, fades
6. **Export**: Saves as WAV files

### Model Architecture

Demucs uses a U-Net style architecture:
- **Encoder**: Converts audio to frequency-domain representation
- **Decoder**: Reconstructs individual sources
- **Attention**: Focuses on different frequency bands for each source

## 🚢 Production Deployment

For production, consider:

1. **Cloud Storage**: Upload generated files to S3/CloudFlare instead of local disk
2. **Queue System**: Use Celery/Redis for async processing (separation can take time)
3. **Caching**: Cache model in memory across requests
4. **Rate Limiting**: Prevent abuse with rate limits
5. **Monitoring**: Add logging and error tracking

## 📝 License

This project is for educational purposes. Make sure you have rights to process any audio files you upload.

## 🙏 Credits

- **Demucs**: Source separation model by Facebook Research
- **FastAPI**: Modern Python web framework
- **React**: UI framework

## 🎓 Learning Resources

If you want to understand source separation better:

- [Demucs Paper](https://arxiv.org/abs/2111.03600)
- [Music Source Separation Tutorial](https://source-separation.github.io/tutorial/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Enjoy creating karaoke tracks!** 🎵

