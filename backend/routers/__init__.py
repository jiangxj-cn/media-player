from .search import router as search_router
from .media import router as media_router
from .auth import router as auth_router
from .playlist import router as playlist_router
from .favorites import router as favorites_router
from .history import router as history_router
from .lyric import router as lyric_router
from .download import router as download_router

__all__ = [
    "search_router", "media_router", "auth_router", "playlist_router",
    "favorites_router", "history_router", "lyric_router", "download_router"
]
