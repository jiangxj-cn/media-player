"""
认证路由
提供用户注册、登录、获取用户信息、数据同步等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..models.media import Favorite, History
from ..models.playlist import Playlist, PlaylistItem
from ..schemas.user import (
    UserCreate, UserLogin, UserResponse, Token,
    SyncRequest, SyncResponse, ErrorResponse
)
from ..utils.auth import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password,
    get_current_user,
    require_user
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=UserResponse, responses={400: {"model": ErrorResponse}})
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    注册新用户
    
    - 用户名: 3-20 字符，仅支持字母、数字和下划线
    - 密码: 6-50 字符
    """
    # 检查用户名是否存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 创建用户
    db_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token, responses={401: {"model": ErrorResponse}})
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    
    返回 JWT token 和用户信息，token 有效期 7 天
    """
    # 验证用户
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成 JWT
    access_token = create_access_token(user_id=db_user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }


@router.get("/profile", response_model=UserResponse, responses={401: {"model": ErrorResponse}})
async def get_profile(current_user: User = Depends(require_user)):
    """
    获取当前用户信息
    
    需要在 Authorization header 中提供 Bearer token
    """
    return current_user


@router.post("/sync", response_model=SyncResponse, responses={401: {"model": ErrorResponse}})
async def sync_data(
    data: SyncRequest,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """
    同步用户数据
    
    将本地数据与服务器数据合并：
    - 收藏：基于 media_url 去重，保留最新的
    - 历史：基于 media_url 合并，保留最新的播放进度
    - 播放列表：暂不实现（需要更复杂的合并逻辑）
    
    返回合并后的完整数据
    """
    user_id = current_user.id
    
    # === 同步收藏 ===
    # 获取服务器现有收藏
    server_favorites = db.query(Favorite).filter(
        Favorite.user_id == user_id
    ).all()
    server_fav_urls = {f.media_url: f for f in server_favorites}
    
    # 添加本地收藏（不存在于服务器的）
    for local_fav in data.favorites:
        media_url = local_fav.get("media_url")
        if media_url and media_url not in server_fav_urls:
            db_favorite = Favorite(
                user_id=user_id,
                media_url=media_url,
                title=local_fav.get("title", ""),
                thumbnail=local_fav.get("thumbnail"),
                source=local_fav.get("source")
            )
            db.add(db_favorite)
            server_fav_urls[media_url] = db_favorite
    
    db.commit()
    
    # 重新获取所有收藏
    all_favorites = db.query(Favorite).filter(
        Favorite.user_id == user_id
    ).order_by(Favorite.created_at.desc()).all()
    
    favorites_list = [
        {
            "id": f.id,
            "media_url": f.media_url,
            "title": f.title,
            "thumbnail": f.thumbnail,
            "source": f.source,
            "created_at": f.created_at.isoformat() if f.created_at else None
        }
        for f in all_favorites
    ]
    
    # === 同步历史 ===
    # 获取服务器现有历史
    server_history = db.query(History).filter(
        History.user_id == user_id
    ).all()
    server_hist_urls = {h.media_url: h for h in server_history}
    
    # 合并本地历史
    for local_hist in data.history:
        media_url = local_hist.get("media_url")
        if media_url:
            if media_url in server_hist_urls:
                # 更新现有记录（如果本地进度更新）
                existing = server_hist_urls[media_url]
                local_position = local_hist.get("position", 0)
                if local_position > existing.position:
                    existing.position = local_position
                    if local_hist.get("duration"):
                        existing.duration = local_hist.get("duration")
            else:
                # 创建新记录
                db_history = History(
                    user_id=user_id,
                    media_url=media_url,
                    title=local_hist.get("title", ""),
                    thumbnail=local_hist.get("thumbnail"),
                    position=local_hist.get("position", 0),
                    duration=local_hist.get("duration")
                )
                db.add(db_history)
    
    db.commit()
    
    # 重新获取所有历史
    all_history = db.query(History).filter(
        History.user_id == user_id
    ).order_by(History.last_played_at.desc()).all()
    
    history_list = [
        {
            "id": h.id,
            "media_url": h.media_url,
            "title": h.title,
            "thumbnail": h.thumbnail,
            "position": h.position,
            "duration": h.duration,
            "last_played_at": h.last_played_at.isoformat() if h.last_played_at else None
        }
        for h in all_history
    ]
    
    # === 同步播放列表 ===
    # 播放列表同步比较复杂，这里简化处理：
    # - 获取服务器的播放列表
    # - 本地新增的播放列表添加到服务器
    # - 返回合并后的列表
    
    server_playlists = db.query(Playlist).filter(
        Playlist.user_id == user_id
    ).all()
    server_playlist_names = {p.name: p for p in server_playlists}
    
    for local_playlist in data.playlists:
        playlist_name = local_playlist.get("name")
        if playlist_name and playlist_name not in server_playlist_names:
            # 创建新播放列表
            db_playlist = Playlist(
                user_id=user_id,
                name=playlist_name
            )
            db.add(db_playlist)
            db.flush()  # 获取 ID
            
            # 添加播放列表项
            for idx, item in enumerate(local_playlist.get("items", [])):
                db_item = PlaylistItem(
                    playlist_id=db_playlist.id,
                    media_url=item.get("media_url", ""),
                    title=item.get("title", ""),
                    thumbnail=item.get("thumbnail"),
                    source=item.get("source"),
                    position=idx
                )
                db.add(db_item)
            
            server_playlist_names[playlist_name] = db_playlist
    
    db.commit()
    
    # 重新获取所有播放列表
    all_playlists = db.query(Playlist).filter(
        Playlist.user_id == user_id
    ).all()
    
    playlists_list = []
    for p in all_playlists:
        items = db.query(PlaylistItem).filter(
            PlaylistItem.playlist_id == p.id
        ).order_by(PlaylistItem.position).all()
        
        playlists_list.append({
            "id": p.id,
            "name": p.name,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            "items": [
                {
                    "id": item.id,
                    "media_url": item.media_url,
                    "title": item.title,
                    "thumbnail": item.thumbnail,
                    "source": item.source,
                    "position": item.position,
                    "added_at": item.added_at.isoformat() if item.added_at else None
                }
                for item in items
            ]
        })
    
    return {
        "favorites": favorites_list,
        "history": history_list,
        "playlists": playlists_list
    }