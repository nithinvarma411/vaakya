import asyncio
import os
from app.services.transcription_service import TranscriptionService

async def main():
    # Initialize add run the transciption service 

    service = TranscriptionService()
    # Need Application logic here 
    # For now, just testing connection
    try:
        # This will test the connection without sending audio
        await service.client.connect()
        print("Connection to Wyoming server successful.")
        await service.client.close()
    except Exception as e:
        print(f"Failed to connect to Wyoming server: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    
  