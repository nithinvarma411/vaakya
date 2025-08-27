from pydantic import BaseModel
from typing import Optional, Dict, Any

class WyomingHeader(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None
    data_length: Optional[int] = None
    payload_length: Optional[int] = None

class TranscribeEvent(BaseModel):
    language: Optional[str] = None
    beam_size: Optional[int] = None
    model: Optional[str] = None