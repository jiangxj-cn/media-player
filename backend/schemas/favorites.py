from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class FavoriteCreate(BaseModel):
    media_url: str
    title: str
    thumbnail: Optional[str] = None
    source: Optional[str] = None

class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    media_url: str
    title: str
    thumbnail: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime

class FavoriteListResponse(BaseModel):
    total: int
    favorites: List[FavoriteResponse]
