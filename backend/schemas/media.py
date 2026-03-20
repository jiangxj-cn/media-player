from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MediaInfo(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    direct_url: Optional[str] = None
    audio_url: Optional[str] = None
    formats: List[dict] = []

class SearchResult(BaseModel):
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    uploader: Optional[str] = None
    source: str = "unknown"

class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[SearchResult]
