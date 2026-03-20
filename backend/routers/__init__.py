from .search import router as search_router
from .media import router as media_router
from .auth import router as auth_router
from .playlist import router as playlist_router

__all__ = ["search_router", "media_router", "auth_router", "playlist_router"]
