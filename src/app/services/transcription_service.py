import asyncio
from typing import Optional
import whisper
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
            print("Loading Whisper base model (multilingual)...")
            # Explicitly use FP32 to avoid warnings on CPU and specify download location
            if TranscriptionService._model is None:
                TranscriptionService._model = whisper.load_model("base", device="cpu")
            self.model = TranscriptionService._model
            print("Whisper base model loaded successfully! (Multilingual)")
            self.initialized = True

    async def transcribe_file(self, file_path: str) -> Optional[str]:
        """Transcribe an audio file using local Whisper"""
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
            # Transcribe the audio file with FP32 explicitly
            # The base model is multilingual and will auto-detect language
            result = self.model.transcribe(file_path, fp16=False)
            transcription = result["text"]
            print(f"Transcription completed: {transcription}")
            # Ensure transcription is a string before calling strip()
            if isinstance(transcription, str):
                return transcription.strip()
            else:
                # Handle case where transcription might be a list or other type
                return str(transcription).strip()
        except Exception as e:
            print(f"Error in synchronous transcription: {e}")
            raise

    async def transcribe_stream(self, audio_stream):
        """Transcribe audio stream in real time"""
        # Implementation for real-time streaming transcription
        pass
