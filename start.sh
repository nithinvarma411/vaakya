#!/bin/bash

# Vaakya - Speech Transcription Service Startup Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Vaakya Speech Transcription Service..."

# Detect OS and set variables
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    OPEN_CMD="open"
    ACTIVATE_CMD="source .venv/bin/activate"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    OPEN_CMD="xdg-open"
    ACTIVATE_CMD="source .venv/bin/activate"
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
    # Windows Git Bash / Cygwin
    OPEN_CMD="start"
    ACTIVATE_CMD="source .venv/Scripts/activate"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

# Start the FastAPI server in the background
echo "⚡ Starting FastAPI server..."
eval "$ACTIVATE_CMD"
PYTHONPATH="$SCRIPT_DIR" uvicorn src.app.api.server:app --host 0.0.0.0 --port 8000 --reload &

# Wait for the server to start
sleep 3

# Open the web interface
echo "🌐 Opening web interface..."
$OPEN_CMD index.html

echo "✅ Vaakya is now running!"
echo "   - Web interface: index.html"
echo "   - API documentation: http://localhost:8000/docs"
echo "   - Local Faster-Whisper processing (no Docker required)"
