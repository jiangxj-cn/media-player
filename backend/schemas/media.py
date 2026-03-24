from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MediaInfo(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    source: Optional[str] = None
    original_url: Optional[str] = None
    direct_url: Optional[str] = None
    audio_url: Optional[str] = None
    embed_url: Optional[str] = None  # iframe 嵌入地址
    use_embed: bool = False  # 是否使用 iframe 播放
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