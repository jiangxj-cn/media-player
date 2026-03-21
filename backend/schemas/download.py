from pydantic import BaseModel
from typing import Optional

class DownloadRequest(BaseModel):
    url: str
    format: str = "video"  # video, audio, best

class DownloadResponse(BaseModel):
    success: bool
    download_url: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None
