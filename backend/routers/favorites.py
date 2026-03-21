"""
收藏路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..models.media import Favorite
from ..schemas.favorites import FavoriteCreate, FavoriteResponse, FavoriteListResponse
from ..utils.auth import get_current_user, require_user

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("/", response_model=FavoriteListResponse)
async def get_favorites(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取收藏列表"""
    user_id = current_user.id if current_user else "anonymous"
    
    favorites = db.query(Favorite).filter(
        Favorite.user_id == user_id
    ).order_by(Favorite.created_at.desc()).all()
    
    return {
        "total": len(favorites),
        "favorites": favorites
    }


@router.post("/", response_model=FavoriteResponse)
async def add_favorite(
    favorite: FavoriteCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加收藏"""
    user_id = current_user.id if current_user else "anonymous"
    
    # 检查是否已收藏
    existing = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.media_url == favorite.media_url
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already favorited"
        )
    
    db_favorite = Favorite(
        user_id=user_id,
        media_url=favorite.media_url,
        title=favorite.title,
        thumbnail=favorite.thumbnail,
        source=favorite.source
    )
    
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    
    return db_favorite


@router.delete("/{favorite_id}")
async def remove_favorite(
    favorite_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    user_id = current_user.id if current_user else "anonymous"
    
    favorite = db.query(Favorite).filter(
        Favorite.id == favorite_id,
        Favorite.user_id == user_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Favorite removed", "id": favorite_id}