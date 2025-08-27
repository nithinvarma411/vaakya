import wave
from ..config.settings import settings

class AudioProcessor:
    @staticmethod
    def convert_to_wav(input_file: str, output_file: str):
        """Convert audio file to required WAV format"""
        # Implementation for audio conversion
        # This would typically use a library like pydub
        pass

    @staticmethod
    def chunk_audio(file_path: str, chunk_size: int):
        """Generator to yield audio chunks"""
        with wave.open(file_path, 'rb') as wf:
            # Check if audio is in correct format
            if (wf.getframerate() != settings.AUDIO_SAMPLE_RATE or
                wf.getnchannels() != settings.AUDIO_CHANNELS or
                wf.getsampwidth() != settings.AUDIO_SAMPLE_WIDTH):
                raise ValueError("Audio format doesn't match required settings")

            # Read and yield chunks
            while True:
                data = wf.readframes(chunk_size)
                if not data:
                    break
                yield data
