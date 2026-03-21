from pydantic import BaseModel
from typing import Optional

class LyricRequest(BaseModel):
    url: str
    source: str = "netease"  # netease, qq, kugou

class LyricResponse(BaseModel):
    url: str
    source: str
    lrc: Optional[str] = None
    error: Optional[str] = None
