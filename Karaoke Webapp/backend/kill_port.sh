#!/bin/bash

# Script to kill any process using port 8000

PORT=8000

echo "🔍 Checking for processes on port $PORT..."

PID=$(lsof -ti:$PORT)

if [ -z "$PID" ]; then
    echo "✅ Port $PORT is free!"
else
    echo "⚠️  Found process $PID using port $PORT"
    echo "🛑 Killing process $PID..."
    kill -9 $PID
    sleep 1
    
    # Verify it's gone
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo "❌ Failed to kill process. Trying force kill..."
        kill -9 $PID 2>/dev/null
    else
        echo "✅ Port $PORT is now free!"
    fi
fi

