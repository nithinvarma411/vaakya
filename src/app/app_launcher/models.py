from pydantic import BaseModel
from typing import List, Dict

class OpenRequest(BaseModel):
    text: str

class OpenResponse(BaseModel):
    name: str
    path: str
    type: str

# New models for list_system
class FolderInfo(BaseModel):
    path: str
    folders: List[str]

class SystemScanResponse(BaseModel):
    apps: Dict[str, str]
    folders: Dict[str, FolderInfo]
