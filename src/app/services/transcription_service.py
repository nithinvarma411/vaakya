import asyncio
from typing import Optional
from faster_whisper import WhisperModel
import tempfile
import os
from .audio_processor import AudioProcessor

class TranscriptionService:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranscriptionService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if not hasattr(self, 'initialized'):
            self.audio_processor = AudioProcessor()
            # Load the Whisper model once during initialization
            print("Loading Faster-Whisper base model (multilingual)...")
            # Use faster-whisper with CPU optimization
            if TranscriptionService._model is None:
                # Using CPU with int8 quantization for better performance
                TranscriptionService._model = WhisperModel("base", device="cpu", compute_type="int8")
            self.model = TranscriptionService._model
            print("Faster-Whisper base model loaded successfully! (Multilingual)")
            self.initialized = True

    async def transcribe_file(self, file_path: str) -> Optional[str]:
        """Transcribe an audio file using Faster-Whisper"""
        try:
            # Convert the audio file to proper WAV format
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_wav_path = tmp_file.name
            
            try:
                # Convert to WAV format
                self.audio_processor.convert_to_wav(file_path, temp_wav_path)
                
                # Use asyncio to run the CPU-intensive transcription in a thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    self._transcribe_sync, 
                    temp_wav_path
                )
                return result
            finally:
                # Clean up temporary file
                if os.path.exists(temp_wav_path):
                    os.unlink(temp_wav_path)
                
        except Exception as e:
            print(f"Error transcribing file: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _transcribe_sync(self, file_path: str) -> str:
        """Synchronous transcription method to run in thread pool"""
        try:
            print(f"Transcribing file: {file_path}")
            # Transcribe the audio file using faster-whisper
            # The base model is multilingual and will auto-detect language
            segments, info = self.model.transcribe(file_path, beam_size=5)
            # Collect all segments into a single transcription
            transcription = " ".join([segment.text for segment in segments])
            print(f"Transcription completed: {transcription}")
            print(f"Detected language: {info.language}")
            return transcription.strip()
        except Exception as e:
            print(f"Error in synchronous transcription: {e}")
            raise

    async def transcribe_stream(self, audio_stream):
        """Transcribe audio stream in real time"""
        # Implementation for real-time streaming transcription
        pass
