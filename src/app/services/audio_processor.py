import ffmpeg
import wave
from ..config.settings import settings

class AudioProcessor:
    @staticmethod
    def convert_to_wav(input_file: str, output_file: str):
        """Convert audio file to required WAV format using ffmpeg"""
        try:
            # Use ffmpeg to convert to proper WAV format
            (
                ffmpeg
                .input(input_file)
                .output(
                    output_file,
                    format='wav',
                    acodec='pcm_s16le',
                    ar=settings.AUDIO_SAMPLE_RATE,
                    ac=settings.AUDIO_CHANNELS
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            print(f"Converted {input_file} to {output_file}")
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            raise
        except Exception as e:
            print(f"Error converting audio file: {e}")
            raise
            
    @staticmethod
    def chunk_audio(file_path: str, chunk_size: int):
        """Generator to yield audio chunks"""
        try:
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
        except Exception as e:
            print(f"Error chunking audio file: {e}")
            raise
