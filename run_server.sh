#!/bin/bash

# Run the FastAPI server with uvicorn
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set Python path to include the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the server on port 8000 to avoid conflicts
uvicorn src.app.api.server:app --host 0.0.0.0 --port 8000 --reload