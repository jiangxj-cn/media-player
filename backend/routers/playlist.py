from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.playlist import Playlist, PlaylistItem
from ..schemas.playlist import PlaylistCreate, PlaylistItemCreate, PlaylistResponse, PlaylistItemResponse

router = APIRouter(prefix="/api/playlist", tags=["playlist"])

@router.post("/", response_model=PlaylistResponse)
async def create_playlist(playlist: PlaylistCreate, db: Session = Depends(get_db)):
    # 这里需要用户认证，暂时创建匿名播放列表
    db_playlist = Playlist(
        user_id="anonymous",
        name=playlist.name
    )
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(playlist_id: str, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist

@router.post("/{playlist_id}/items", response_model=PlaylistItemResponse)
async def add_item(playlist_id: str, item: PlaylistItemCreate, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # 获取当前位置
    max_position = db.query(PlaylistItem.position).filter(
        PlaylistItem.playlist_id == playlist_id
    ).count()
    
    db_item = PlaylistItem(
        playlist_id=playlist_id,
        media_url=item.media_url,
        title=item.title,
        thumbnail=item.thumbnail,
        source=item.source,
        position=max_position
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{playlist_id}/items", response_model=List[PlaylistItemResponse])
async def get_playlist_items(playlist_id: str, db: Session = Depends(get_db)):
    items = db.query(PlaylistItem).filter(
        PlaylistItem.playlist_id == playlist_id
    ).order_by(PlaylistItem.position).all()
    return items
