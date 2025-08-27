import asyncio
import struct
import json
from typing import Optional
from ..config.settings import settings
from ..models.wyoming_events import WyomingHeader

class WyomingClient:
    def __init__(self):
        self.host = settings.WYOMING_HOST
        self.port = settings.WYOMING_PORT
        self.reader = None
        self.writer = None

    async def connect(self):
        # Establish connection to Wyoming server 
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            print(f"Connected to Wyoming server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Wyoming server: {e}")
            raise

    async def send_event(self, header: WyomingHeader, payload: Optional[bytes] = None):
        # Send event to Wyoming server
        if not self.writer:
            raise ConnectionError("Not connected to Wyoming server")
        
        # Serialize header to JSON 
        header_json = header.json(exclude_none=True)
        header_bytes = header_json.encode('utf-8')
        header_length = len(header_bytes)

        # Send header length (4 bytes, big endian)
        self.writer.write(struct.pack('>I', header_length))

        # Send header
        self.writer.write(header_bytes)

        # Send payload if provided 
        if payload:
            self.writer.write(payload)
        
        await self.writer.drain()

    async def receive_event(self):
        # Receive event from Wyoming server 
        if not self.reader:
            raise ConnectionError("Not connected to Wyoming server")
        
        try:
            # Read header length (4 bytes)
            header_length_bytes = await self.reader.readexactly(4)
            header_length = struct.unpack('>I', header_length_bytes)[0]

            # Read header
            header_bytes = await self.reader.readexactly(header_length)
            header_data = json.loads(header_bytes.decode('utf-8'))
            header = WyomingHeader(**header_data)

            # Read payload if present 
            payload = None
            if header.payload_length and header.payload_length > 0:
                payload = await self.reader.readexactly(header.payload_length)
            return header, payload
        except Exception as e:
            print(f"Error receiving event: {e}")
            raise

    async def close(self):
        # Close connection
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.reader = None
            self.writer = None
        print("Connection closed")



