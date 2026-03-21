"""
认证工具函数
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt

from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS
from ..database import get_db
from ..models.user import User

security = HTTPBearer(auto_error=False)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌
    
    Args:
        user_id: 用户 ID
        expires_delta: 过期时间间隔，默认使用配置中的天数
    
    Returns:
        JWT token 字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    验证 JWT 令牌
    
    Args:
        token: JWT token 字符串
    
    Returns:
        用户 ID，如果验证失败返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    """
    对密码进行 bcrypt 加密
    
    Args:
        password: 明文密码
    
    Returns:
        加密后的密码哈希
    """
    # bcrypt 需要字节输入
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """
    验证密码是否匹配
    
    Args:
        plain: 明文密码
        hashed: 哈希后的密码
    
    Returns:
        是否匹配
    """
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    从请求中获取当前用户
    
    Args:
        credentials: HTTP Bearer 凭证
        db: 数据库会话
    
    Returns:
        User 对象，如果未认证返回 None
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


def require_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    要求用户必须登录
    
    Args:
        current_user: 当前用户
    
    Returns:
        User 对象
    
    Raises:
        HTTPException: 如果用户未登录
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user