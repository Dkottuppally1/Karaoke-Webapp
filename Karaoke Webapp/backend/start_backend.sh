#!/bin/bash

# Script to start the backend server

cd "$(dirname "$0")"

echo "🎤 Starting Karaoke Generator Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check NumPy version
NUMPY_VERSION=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null)
if [[ "$NUMPY_VERSION" == 2.* ]]; then
    echo "⚠️  NumPy 2.x detected. Downgrading to 1.x..."
    pip install "numpy<2.0.0" --force-reinstall --no-cache-dir
fi

echo ""
echo "🚀 Starting server on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the server
python app.py

