import os

class Settings:
    # Audio setting 
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_SAMPLE_WIDTH = 2

    # Transcription settings 
    DEFAULT_BEAM_SIZE = 5
    DEFAULT_LANGUAGE = "auto"

settings = Settings()


