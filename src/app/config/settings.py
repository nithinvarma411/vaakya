import os

class Settings:
    # Wyoming server settings 
    WYOMING_HOST = os.getenv("WYOMING_HOST", "localhost")
    WYOMING_PORT = int(os.getenv("WYOMING_PORT", 10300))
    # WYOMING_DEBUG = os.getenv("WYOMING_DEBUG", "true").lower() == "true"

    # Audio setting 
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_SAMPLE_WIDTH = 2

    # Transcription settings 
    DEFAULT_BEAM_SIZE = 5
    DEFAULT_LANGUAGE = "auto"

settings = Settings()


