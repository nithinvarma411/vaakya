import asyncio

from src.app.services.transcription_service import TranscriptionService


async def main() -> None:
    # Initialize and run the transcription service
    _service = TranscriptionService()

    # Need Application logic here
    # For now, just testing the service initialization
    print("Transcription service initialized successfully.")

    # Example usage (uncomment when you have an audio file to test):
    # transcription = await _service.transcribe_file("path/to/audio/file.wav")
    # print(f"Transcription: {transcription}")


if __name__ == "__main__":
    asyncio.run(main())
