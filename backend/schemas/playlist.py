from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PlaylistCreate(BaseModel):
    name: str

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None

class PlaylistItemCreate(BaseModel):
    media_url: str
    title: str
    thumbnail: Optional[str] = None
    source: Optional[str] = None

class PlaylistItemUpdate(BaseModel):
    position: int

class PlaylistReorderRequest(BaseModel):
    item_id: str
    new_position: int

class PlaylistResponse(BaseModel):
    id: str
    user_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    items: Optional[List["PlaylistItemResponse"]] = None
    
    class Config:
        from_attributes = True

class PlaylistItemResponse(BaseModel):
    id: str
    playlist_id: str
    media_url: str
    title: str
    thumbnail: Optional[str] = None
    source: Optional[str] = None
    position: int
    added_at: datetime
    
    class Config:
        from_attributes = True

class PlaylistListResponse(BaseModel):
    total: int
    playlists: List[PlaylistResponse]
