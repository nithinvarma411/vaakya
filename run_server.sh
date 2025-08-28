#!/bin/bash

# Run the FastAPI server with uvicorn
cd "$(dirname "$0")"

# Activate virtual environment, works on both linux and windows
if [ -d ".venv" ]; then
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        source .venv/bin/activate
    elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
        source .venv/Scripts/activate
    fi
fi

# Set Python path to include the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the server on port 8000 to avoid conflicts
uvicorn src.app.api.server:app --host 0.0.0.0 --port 8000 --reload
