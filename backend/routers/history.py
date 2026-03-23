"""
历史记录路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..models.media import History
from ..schemas.history import HistoryCreate, HistoryResponse, HistoryListResponse
from ..utils.auth import get_current_user, require_user

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/", response_model=HistoryListResponse)
async def get_history(
    limit: int = 50,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取历史记录"""
    user_id = current_user.id if current_user else "anonymous"
    
    history = db.query(History).filter(
        History.user_id == user_id
    ).order_by(History.last_played_at.desc()).limit(limit).all()
    
    return {
        "total": len(history),
        "history": history
    }


@router.post("/", response_model=HistoryResponse)
async def record_history(
    history: HistoryCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录播放（更新进度）"""
    user_id = current_user.id if current_user else "anonymous"
    
    # 检查是否已存在
    existing = db.query(History).filter(
        History.user_id == user_id,
        History.media_url == history.media_url
    ).first()
    
    if existing:
        # 更新现有记录
        existing.position = history.position
        if history.duration is not None:
            existing.duration = history.duration
        existing.last_played_at = func.now()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # 创建新记录
        db_history = History(
            user_id=user_id,
            media_url=history.media_url,
            title=history.title,
            thumbnail=history.thumbnail,
            position=history.position,
            duration=history.duration
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history


@router.delete("/")
async def clear_history(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空历史"""
    user_id = current_user.id if current_user else "anonymous"
    
    db.query(History).filter(
        History.user_id == user_id
    ).delete()
    db.commit()
    
    return {"message": "History cleared"}