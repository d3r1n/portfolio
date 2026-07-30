from .admin import router as admin_router
from .auth import router as auth_router
from .books import router as books_router
from .location import router as location_router
from .projects import router as projects_router
from .spotify import router as spotify_router

all_routers = [books_router, projects_router, spotify_router, location_router, auth_router, admin_router]

__all__ = [
	"admin_router",
	"auth_router",
	"books_router",
	"location_router",
	"projects_router",
	"spotify_router",
	"all_routers",
]
