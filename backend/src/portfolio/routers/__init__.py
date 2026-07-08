from .auth import router as auth_router
from .books import router as books_router
from .projects import router as projects_router
from .spotify import router as spotify_router

__all__ = ["books_router", "projects_router", "spotify_router", "auth_router"]
