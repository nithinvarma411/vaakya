import asyncio
from typing import Optional
from .wyoming_client import WyomingClient
from .audio_processor import AudioProcessor
from ..config.settings import settings
from ..models.wyoming_events import WyomingHeader, TranscribeEvent

class TranscriptionService:
    def __init__(self):
        self.client = WyomingClient()
        self.audio_processor = AudioProcessor()

    async def transcribe_file(self, file_path: str) -> Optional[str]:
        # Transcribe an audio file 
        try:
            await self.client.connect()

            # Send transcribe event 
            transcribe_event = TranscribeEvent(
                language = settings.DEFAULT_LANGUAGE,
                beam_size = settings.DEFAULT_BEAM_SIZE
            )

            header = WyomingHeader(
                type="transcribe",
                data = transcribe_event.dict(exclude_none=True)
            )

            # Read audio file 
            with open(file_path, 'rb') as f:
                audio_data = f.read()

            header.payload_length = len(audio_data)
            await self.client.send_event(header, audio_data)

            # Receive transcription result 
            result_header, result_payload = await self.client.receive_event()

            if result_header.type == "transcription":
                transcription = result_payload.decode('utf-8') if result_payload else ""
                return transcription
            else:
                print(f"Unexpected response type: {result_header.type}")
                return None
            
        except Exception as e:
            print(f"Error transcribing file: {e}")
            return None
        finally:
            await self.client.close()


    async def transcribe_stream(self, audio_stream):
        # Transcribe audio stream in real time 
        pass
