from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import uuid

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    items = relationship("PlaylistItem", back_populates="playlist", cascade="all, delete-orphan")

class PlaylistItem(Base):
    __tablename__ = "playlist_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    playlist_id = Column(String, ForeignKey("playlists.id"), nullable=False)
    media_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    thumbnail = Column(String)
    source = Column(String)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime, server_default=func.now())
    
    playlist = relationship("Playlist", back_populates="items")
