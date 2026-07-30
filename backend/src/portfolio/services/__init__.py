from typing import Any, Callable, Coroutine

from ..database import Database
from .init_location import init_current_location
from .init_projects import init_default_projects
from .initialize_admin import init_admin_user


def db_init_services() -> list[Callable[[Database], Coroutine[Any, Any, None]]]:
	"""
	Returns a list of database initialization services to be run at application startup.
	Each takes the database facade, so they stay independent of the concrete backend.
	"""
	return [init_admin_user, init_current_location, init_default_projects]
