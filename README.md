
## Current Features
- File-based transcription with local Whisper model
- Web interface for live audio recording and transcription
- FastAPI backend with automatic API documentation
- Fully local processing - no external dependencies or internet required
- Optimized for CPU with FP32 precision to avoid warnings

## Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Web Browser   │◄──►│   FastAPI Server │◄──►│  Whisper Model      │
│  (index.html)   │    │  (server.py)     │    │  (Local Processing) │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Prerequisites
- Python 3.8+
- uv (for dependency management)
- ffmpeg (for audio processing)

## Setup

1. Install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

2. Install ffmpeg:
   ```bash
   # On macOS:
   brew install ffmpeg
   
   # On Ubuntu/Debian:
   sudo apt-get install ffmpeg
   
   # On Windows:
   # Download from https://ffmpeg.org/download.html
   ```

3. Start the FastAPI server (in a new terminal):
   ```bash
   ./run_server.sh
   ```

4. Open `index.html` in your browser to use the web interface

## API Endpoints

- `GET /` - Health check
- `POST /transcribe` - Transcribe uploaded audio file
- `GET /docs` - Interactive API documentation

## Usage

1. Open `index.html` in your browser
2. Click "Start Recording" and speak into your microphone
3. The audio will be processed locally using Whisper
4. The transcription will appear in the text area

You can also use the API directly:
```bash
curl -X POST "http://localhost:8000/transcribe" -F "audio=@your_audio_file.wav"
```

## Model Information

The application uses OpenAI's Whisper model for transcription:
- Model: `base` (better accuracy than tiny, still good for real-time)
- Precision: FP32 (avoids CPU warnings)
- Multilingual support for speech recognition, translation, and language identification

To change the model, modify this line in `src/app/services/transcription_service.py`:
```python
self.model = whisper.load_model("base", device="cpu")  # Change to "small", "medium", or "large" for better accuracy
```

## Project Structure
```
vaakya/
├── index.html                  # Web interface
├── requirements.txt            # Python dependencies
├── run_server.sh              # Script to run FastAPI server
├── start.sh                   # Full application startup script
├── src/
│   ├── main.py                 # CLI entry point
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── server.py       # FastAPI server
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py     # Configuration settings
│   │   ├── models/
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── audio_processor.py     # Audio processing with ffmpeg
│   │   │   ├── transcription_service.py  # Local Whisper transcription
│   │   └── utils/
│   │       └── __init__.py
│   └── tests/
│       └── __init__.py
```
