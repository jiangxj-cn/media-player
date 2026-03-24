from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import List, Optional


class UserCreate(BaseModel):
    username: str
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 20:
            raise ValueError('Username must be between 3 and 20 characters')
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6 or len(v) > 50:
            raise ValueError('Password must be between 6 and 50 characters')
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class SyncRequest(BaseModel):
    favorites: List[dict] = []
    history: List[dict] = []
    playlists: List[dict] = []


class SyncResponse(BaseModel):
    favorites: List[dict] = []
    history: List[dict] = []
    playlists: List[dict] = []


class ErrorResponse(BaseModel):
    detail: str