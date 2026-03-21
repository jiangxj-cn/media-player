from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.user import User
from ..models.playlist import Playlist, PlaylistItem
from ..schemas.playlist import (
    PlaylistCreate, PlaylistUpdate, PlaylistItemCreate, PlaylistItemUpdate,
    PlaylistReorderRequest, PlaylistResponse, PlaylistItemResponse, PlaylistListResponse
)

router = APIRouter(prefix="/api/playlists", tags=["playlists"])

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """获取当前用户（可选认证）"""
    if not authorization:
        return {"id": "anonymous", "username": "anonymous"}
    
    try:
        from jose import jwt
        from ..config import SECRET_KEY, ALGORITHM
        
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            return {"id": "anonymous", "username": "anonymous"}
        
        user = db.query(User).filter(User.username == username).first()
        if user:
            return {"id": user.id, "username": user.username}
        return {"id": "anonymous", "username": "anonymous"}
    except Exception:
        return {"id": "anonymous", "username": "anonymous"}

@router.get("/", response_model=PlaylistListResponse)
async def get_playlists(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有播放列表"""
    playlists = db.query(Playlist).filter(
        Playlist.user_id == user["id"]
    ).order_by(Playlist.created_at.desc()).all()
    
    return {
        "total": len(playlists),
        "playlists": playlists
    }

@router.post("/", response_model=PlaylistResponse)
async def create_playlist(
    playlist: PlaylistCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建播放列表"""
    db_playlist = Playlist(
        user_id=user["id"],
        name=playlist.name
    )
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@router.get("/{id}", response_model=PlaylistResponse)
async def get_playlist(
    id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取播放列表详情"""
    playlist = db.query(Playlist).filter(
        Playlist.id == id,
        Playlist.user_id == user["id"]
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # 加载播放列表项
    playlist.items = db.query(PlaylistItem).filter(
        PlaylistItem.playlist_id == id
    ).order_by(PlaylistItem.position).all()
    
    return playlist

@router.put("/{id}", response_model=PlaylistResponse)
async def update_playlist(
    id: str,
    playlist: PlaylistUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新播放列表"""
    db_playlist = db.query(Playlist).filter(
        Playlist.id == id,
        Playlist.user_id == user["id"]
    ).first()
    
    if not db_playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    if playlist.name is not None:
        db_playlist.name = playlist.name
    
    db_playlist.updated_at = db.func.now()
    db.commit()
    db.refresh(db_playlist)
    
    return db_playlist

@router.delete("/{id}")
async def delete_playlist(
    id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除播放列表"""
    db_playlist = db.query(Playlist).filter(
        Playlist.id == id,
        Playlist.user_id == user["id"]
    ).first()
    
    if not db_playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    db.delete(db_playlist)
    db.commit()
    
    return {"message": "Playlist deleted", "id": id}

@router.post("/{id}/items", response_model=PlaylistItemResponse)
async def add_item(
    id: str,
    item: PlaylistItemCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加项到播放列表"""
    playlist = db.query(Playlist).filter(
        Playlist.id == id,
        Playlist.user_id == user["id"]
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # 获取当前位置
    max_position = db.query(PlaylistItem.position).filter(
        PlaylistItem.playlist_id == id
    ).count()
    
    db_item = PlaylistItem(
        playlist_id=id,
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

@router.delete("/{id}/items/{item_id}")
async def remove_item(
    id: str,
    item_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从播放列表移除项"""
    playlist = db.query(Playlist).filter(
        Playlist.id == id,
        Playlist.user_id == user["id"]
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    item = db.query(PlaylistItem).filter(
        PlaylistItem.id == item_id,
        PlaylistItem.playlist_id == id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item removed", "id": item_id}

@router.put("/{id}/reorder")
async def reorder_items(
    id: str,
    reorder_request: PlaylistReorderRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重新排序播放列表项"""
    playlist = db.query(Playlist).filter(
        Playlist.id == id,
        Playlist.user_id == user["id"]
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    item = db.query(PlaylistItem).filter(
        PlaylistItem.id == reorder_request.item_id,
        PlaylistItem.playlist_id == id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # 更新位置
    old_position = item.position
    new_position = reorder_request.new_position
    
    if old_position < new_position:
        # 向下移动：将中间项上移
        db.query(PlaylistItem).filter(
            PlaylistItem.playlist_id == id,
            PlaylistItem.position > old_position,
            PlaylistItem.position <= new_position
        ).update(
            {"position": PlaylistItem.position - 1},
            synchronize_session=False
        )
    else:
        # 向上移动：将中间项下移
        db.query(PlaylistItem).filter(
            PlaylistItem.playlist_id == id,
            PlaylistItem.position >= new_position,
            PlaylistItem.position < old_position
        ).update(
            {"position": PlaylistItem.position + 1},
            synchronize_session=False
        )
    
    item.position = new_position
    db.commit()
    db.refresh(item)
    
    return {"message": "Item reordered", "item_id": item_id, "new_position": new_position}
