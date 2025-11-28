# How to Connect to the API

Your backend is **already running** and accessible! Here's how to connect:

## ✅ Backend Status

From your terminal output, I can see:
- ✅ Server is running on `http://0.0.0.0:8000`
- ✅ Model is loaded successfully
- ✅ Health check endpoint is working
- ✅ API is ready to accept requests

## 🔗 Connection Methods

### Method 1: Frontend (Recommended)

1. **Start the frontend** (in a new terminal):
   ```bash
   cd "/Users/dkottuppally/Karaoke Webapp/frontend"
   npm install  # if you haven't already
   npm run dev
   ```

2. **Open your browser** to the URL shown (usually `http://localhost:3000`)

3. The frontend will automatically connect to the backend at `http://localhost:8000`

### Method 2: Direct API Testing (Browser)

Open these URLs in your browser:

- **Health Check**: `http://localhost:8000/api/health`
- **Root Endpoint**: `http://localhost:8000/`

You should see JSON responses like:
```json
{"status":"healthy","model_loaded":true,"message":"API is ready"}
```

### Method 3: Command Line (curl)

Test the API from terminal:

```bash
# Health check
curl http://localhost:8000/api/health

# Root endpoint
curl http://localhost:8000/

# Test file upload (example)
curl -X POST http://localhost:8000/api/separate \
  -F "file=@/path/to/your/song.mp3"
```

### Method 4: Python Script

Create a test script:

```python
import requests

# Test health endpoint
response = requests.get('http://localhost:8000/api/health')
print(response.json())

# Test file upload
with open('your_song.mp3', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/separate', files=files)
    print(response.json())
```

## 🌐 API Endpoints

Your backend has these endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Basic health check |
| `GET` | `/api/health` | Detailed health check with model status |
| `POST` | `/api/separate` | Upload audio file and separate into stems |
| `GET` | `/api/download/{file_id}` | Download generated audio files |

## 🔧 Connection Details

- **Backend URL**: `http://localhost:8000` or `http://0.0.0.0:8000`
- **Frontend URL**: `http://localhost:3000` (when running `npm run dev`)
- **CORS**: Already configured to allow frontend connections

## ⚠️ Fixing the NumPy Warning

The NumPy warning you see is just a warning - your app is working! But to fix it:

```bash
cd "/Users/dkottuppally/Karaoke Webapp/backend"
source venv/bin/activate
pip install "numpy<2.0.0" --force-reinstall
```

Then restart the backend.

## 🚀 Quick Start

**Easiest way to use the app:**

1. **Keep backend running** (it's already running in your terminal)

2. **Open a new terminal** and start frontend:
   ```bash
   cd "/Users/dkottuppally/Karaoke Webapp/frontend"
   npm run dev
   ```

3. **Open browser** to `http://localhost:3000`

4. **Upload a song** and click "Generate Karaoke"

That's it! The frontend will automatically connect to your backend API.

## 🐛 Troubleshooting

**If frontend can't connect:**

1. Make sure backend is running (check terminal for "Uvicorn running on...")
2. Check backend is on port 8000
3. Check browser console (F12) for errors
4. Try accessing `http://localhost:8000/api/health` directly in browser

**If you see CORS errors:**

The CORS is already configured in `backend/app.py`. Make sure:
- Frontend is on `http://localhost:3000` or `http://localhost:5173`
- Backend allows these origins (already set)

## 📝 Example: Testing with curl

```bash
# 1. Check if API is running
curl http://localhost:8000/api/health

# 2. Upload a file (replace path with your audio file)
curl -X POST http://localhost:8000/api/separate \
  -F "file=@/Users/dkottuppally/Music/song.mp3" \
  -o response.json

# 3. Check the response
cat response.json
```

The response will include download URLs for the separated tracks!

