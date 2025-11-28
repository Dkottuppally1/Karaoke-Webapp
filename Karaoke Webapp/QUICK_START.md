# 🚀 Quick Start Guide

## The Problem
You're seeing: **"⚠️ Cannot connect to backend. Make sure the server is running on http://localhost:8000"**

This means the backend server is not running or not accessible.

## ✅ Solution: Start the Backend

### Method 1: Use the Startup Script (Easiest)

1. **Open a terminal**
2. **Run this command:**
   ```bash
   cd "/Users/dkottuppally/Karaoke Webapp/backend"
   ./start_backend.sh
   ```

3. **Wait for these messages:**
   - "Loading source separation model..."
   - "Model loaded successfully!"
   - "Model loaded and ready!"
   - "Uvicorn running on http://0.0.0.0:8000"

4. **Keep this terminal open** - the server needs to keep running

### Method 2: Manual Start

1. **Open a terminal**
2. **Navigate to backend:**
   ```bash
   cd "/Users/dkottuppally/Karaoke Webapp/backend"
   ```

3. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Start the server:**
   ```bash
   python app.py
   ```

5. **Wait for "Uvicorn running on http://0.0.0.0:8000"**

## 🔍 Verify Backend is Running

**In a NEW terminal**, test the connection:

```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{"status":"healthy","model_loaded":true,"message":"API is ready"}
```

If you get this, the backend is working! ✅

## 🌐 Start the Frontend

**In a NEW terminal** (keep backend running):

```bash
cd "/Users/dkottuppally/Karaoke Webapp/frontend"
npm install  # if you haven't already
npm run dev
```

Then open `http://localhost:3000` in your browser.

## ⚠️ Common Issues

### Issue 1: "Connection refused"
- **Cause**: Backend is not running
- **Fix**: Start the backend (see above)

### Issue 2: NumPy warning
- **Cause**: NumPy 2.x is installed
- **Fix**: The startup script will fix this automatically, or run:
  ```bash
  pip install "numpy<2.0.0" --force-reinstall
  ```

### Issue 3: Port 8000 already in use
- **Cause**: Another process is using port 8000
- **Fix**: 
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```
  Then restart the backend

### Issue 4: Model download fails
- **Cause**: No internet or SSL issues
- **Fix**: Make sure you have internet connection. The model downloads automatically on first run (~1.5GB)

## 📋 Checklist

Before using the app, make sure:

- [ ] Backend is running (you see "Uvicorn running on...")
- [ ] Model is loaded (you see "Model loaded and ready!")
- [ ] Health check works: `curl http://localhost:8000/api/health`
- [ ] Frontend is running: `npm run dev` in frontend directory
- [ ] Browser shows backend status as "✅ Backend Ready"

## 🎯 Step-by-Step (First Time)

1. **Terminal 1 - Start Backend:**
   ```bash
   cd "/Users/dkottuppally/Karaoke Webapp/backend"
   ./start_backend.sh
   ```
   Wait for "Model loaded and ready!"

2. **Terminal 2 - Start Frontend:**
   ```bash
   cd "/Users/dkottuppally/Karaoke Webapp/frontend"
   npm install
   npm run dev
   ```

3. **Browser:**
   - Open `http://localhost:3000`
   - You should see "✅ Backend Ready" at the top
   - Upload a song and click "Generate Karaoke"

## 💡 Pro Tip

Keep two terminal windows open:
- **Terminal 1**: Backend (running `python app.py`)
- **Terminal 2**: Frontend (running `npm run dev`)

Both need to stay running for the app to work!

