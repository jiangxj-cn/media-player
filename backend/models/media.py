from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from ..database import Base
import uuid

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    media_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    thumbnail = Column(String)
    source = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class History(Base):
    __tablename__ = "history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    media_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    thumbnail = Column(String)
    position = Column(Integer, default=0)
    duration = Column(Integer)
    last_played_at = Column(DateTime, server_default=func.now())
