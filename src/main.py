import asyncio
import os
from app.services.transcription_service import TranscriptionService

async def main():
    # Initialize and run the transcription service 
    service = TranscriptionService()
    
    # Need Application logic here 
    # For now, just testing the service initialization
    print("Transcription service initialized successfully.")
    
    # Example usage (uncomment when you have an audio file to test):
    # transcription = await service.transcribe_file("path/to/audio/file.wav")
    # print(f"Transcription: {transcription}")

if __name__ == "__main__":
    asyncio.run(main())
    
  