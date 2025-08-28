import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import asyncio

# Local imports
from src.app.services.transcription_service import TranscriptionService

app = FastAPI(title="Speech Transcription API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the transcription service
transcription_service = TranscriptionService()

# Global variable to track if we've already loaded the model
model_loaded = False

@app.on_event("startup")
async def startup_event():
    global model_loaded
    if not model_loaded:
        print("Application startup complete")
        model_loaded = True

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown initiated")
    # Cleanup code can go here if needed

@app.get("/")
async def root():
    return {"message": "Speech Transcription API is running"}

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            temp_filename = tmp_file.name
        
        try:
            # Transcribe the audio file with timeout
            transcription = await asyncio.wait_for(
                transcription_service.transcribe_file(temp_filename), 
                timeout=120.0  # 2 minute timeout for local processing
            )
            
            # Remove the temporary file
            os.unlink(temp_filename)
            
            if transcription is not None:
                return {"transcription": transcription}
            else:
                raise HTTPException(status_code=500, detail="Transcription failed")
                
        except asyncio.TimeoutError:
            # Remove the temporary file if an error occurred
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise HTTPException(status_code=500, detail="Transcription timeout - audio processing took too long")
        except Exception as e:
            # Remove the temporary file if an error occurred
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request processing error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)