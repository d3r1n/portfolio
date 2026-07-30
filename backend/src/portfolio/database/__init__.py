"""Database facade package.

`get_database()` is the composition root: the one line to change when swapping
the persistence backend. Everything else programs against
`portfolio.database.interface.Database` and the DTOs in `portfolio.database.dto`.
"""

from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from .interface import Database


@lru_cache
def get_database() -> Database:
	# Swap the backend here — nothing else in the app names a concrete implementation.
	from .peewee_backend import PeeweeDatabase

	return PeeweeDatabase()


async def get_db() -> AsyncGenerator[Database, None]:
	"""FastAPI dependency: hold a pooled connection for the duration of the request."""
	db = get_database()
	async with db.session():
		yield db


DatabaseDep = Annotated[Database, Depends(get_db)]

__all__ = ["Database", "DatabaseDep", "get_database", "get_db"]
