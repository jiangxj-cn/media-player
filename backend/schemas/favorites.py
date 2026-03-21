from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class FavoriteCreate(BaseModel):
    media_url: str
    title: str
    thumbnail: Optional[str] = None
    source: Optional[str] = None

class FavoriteResponse(BaseModel):
    id: str
    user_id: str
    media_url: str
    title: str
    thumbnail: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class FavoriteListResponse(BaseModel):
    total: int
    favorites: List[FavoriteResponse]
