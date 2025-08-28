#!/bin/bash

# Vaakya - Speech Transcription Service Stop Script

echo "🛑 Stopping Vaakya Speech Transcription Service..."

# Kill FastAPI server processes
echo "⚡ Stopping FastAPI server..."
pkill -f "uvicorn.*src.app.api.server" || echo "No FastAPI server processes found"

echo "✅ Vaakya services stopped!"