from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.transcription_service import TranscriptionService
import tempfile
import os
import asyncio

app = FastAPI(title="Speech Transcription API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

transcription_service = TranscriptionService()

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            temp_filename = tmp_file.name

        try:
            transcription = await asyncio.wait_for(
                transcription_service.transcribe_file(temp_filename), timeout=120.0
            )
            os.unlink(temp_filename)
            if transcription is not None:
                return {"transcription": transcription}
            else:
                raise HTTPException(status_code=500, detail="Transcription failed")
        except asyncio.TimeoutError:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise HTTPException(status_code=500, detail="Transcription timeout")
        except Exception as e:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request processing error: {str(e)}")
