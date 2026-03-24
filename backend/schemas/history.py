from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class HistoryCreate(BaseModel):
    media_url: str
    title: str
    thumbnail: Optional[str] = None
    position: int = 0
    duration: Optional[int] = None

class HistoryUpdate(BaseModel):
    position: int
    duration: Optional[int] = None

class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    media_url: str
    title: str
    thumbnail: Optional[str] = None
    position: int
    duration: Optional[int] = None
    last_played_at: datetime

class HistoryListResponse(BaseModel):
    total: int
    history: List[HistoryResponse]
