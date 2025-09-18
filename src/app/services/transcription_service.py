import asyncio
import os
import tempfile
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

from faster_whisper import WhisperModel

from src.app.config.settings import settings

from .audio_processor import AudioProcessor


class TranscriptionService:
    _instance = None
    _model = None
    _executor = None

    def __new__(cls) -> "TranscriptionService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once
        if not hasattr(self, "initialized"):
            self.audio_processor = AudioProcessor()

            # Create a dedicated thread pool executor for transcription
            if TranscriptionService._executor is None:
                TranscriptionService._executor = ThreadPoolExecutor(
                    max_workers=2, thread_name_prefix="transcription"
                )
            self.executor = TranscriptionService._executor

            # Load the Whisper model once during initialization
            print("Loading Faster-Whisper base model (multilingual)...")
            # Use faster-whisper with CPU optimization
            if TranscriptionService._model is None:
                # Using CPU with int8 quantization for better performance
                TranscriptionService._model = WhisperModel(
                    settings.model.WHISPER_MODEL_SIZE,
                    device=settings.model.WHISPER_DEVICE,
                    compute_type=settings.model.WHISPER_COMPUTE_TYPE,
                )
            self.model = TranscriptionService._model
            print("Faster-Whisper base model loaded successfully! (Multilingual)")
            self.initialized = True

    def cleanup(self) -> None:
        """Clean up resources used by the transcription service."""
        try:
            # Shutdown the thread pool executor
            if TranscriptionService._executor is not None:
                print("Shutting down transcription thread pool...")
                TranscriptionService._executor.shutdown(wait=True, cancel_futures=True)
                TranscriptionService._executor = None

            # Clean up the model if it exists
            if TranscriptionService._model is not None:
                print("Cleaning up Whisper model resources...")
                # The WhisperModel doesn't have explicit cleanup, but we can clear the reference
                TranscriptionService._model = None

            # Clean up audio processor
            if hasattr(self, "audio_processor"):
                # AudioProcessor cleanup if needed
                pass

            print("TranscriptionService cleanup completed")
        except Exception as e:
            print(f"Error during TranscriptionService cleanup: {e}")

    @classmethod
    def shutdown(cls) -> None:
        """Class method to clean up singleton instance."""
        if cls._instance is not None:
            cls._instance.cleanup()
            cls._instance = None

    async def transcribe_file(self, file_path: str) -> Optional[str]:
        """Transcribe an audio file using Faster-Whisper"""
        try:
            # Convert the audio file to proper WAV format
            with tempfile.NamedTemporaryFile(
                suffix=settings.audio.TEMP_AUDIO_SUFFIX, delete=False
            ) as tmp_file:
                temp_wav_path = tmp_file.name

            try:
                # Convert to WAV format
                self.audio_processor.convert_to_wav(file_path, temp_wav_path)

                # Use our dedicated thread pool executor for transcription
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor, self._transcribe_sync, temp_wav_path
                )
                return result
            finally:
                # Clean up temporary file
                if os.path.exists(temp_wav_path):
                    os.unlink(temp_wav_path)

        except Exception as e:
            print(f"Error transcribing file: {e}")
            traceback.print_exc()
            return None

    def _transcribe_sync(self, file_path: str) -> str:
        """Synchronous transcription method to run in thread pool"""
        try:
            print(f"Transcribing file: {file_path}")
            # Transcribe the audio file using faster-whisper
            # The base model is multilingual and will auto-detect language
            segments, info = self.model.transcribe(
                file_path, beam_size=settings.audio.DEFAULT_BEAM_SIZE
            )
            # Collect all segments into a single transcription
            transcription = " ".join([segment.text for segment in segments])
            print(f"Transcription completed: {transcription}")
            print(f"Detected language: {info.language}")
            return transcription.strip()
        except Exception as e:
            print(f"Error in synchronous transcription: {e}")
            raise

    async def transcribe_stream(self, audio_stream: Any) -> None:
        """Transcribe audio stream in real time"""
        # Implementation for real-time streaming transcription
