"""Abstract database facade.

Callers depend exclusively on the interfaces below. A concrete backend (see
`peewee_backend/`) implements them; switching ORM or database engine means
writing a new implementation package and pointing `get_database()` at it —
nothing outside `portfolio.database` changes.
"""

import uuid
from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Any, Mapping, Sequence

from . import dto


class AdminRepository(ABC):
	"""Admins and their login sessions (Admin is the aggregate root)."""

	@abstractmethod
	async def get_by_username(self, username: str) -> dto.Admin | None: ...

	@abstractmethod
	async def create(self, *, user: str, email: str, hashed_password: str) -> dto.Admin: ...

	@abstractmethod
	async def create_session(
		self,
		*,
		admin_id: uuid.UUID,
		jti: str,
		expires_at: datetime,
		user_agent: str | None = None,
		ip_address: str | None = None,
	) -> dto.AdminSession: ...

	@abstractmethod
	async def get_by_valid_session(self, admin_id: uuid.UUID, jti: str) -> dto.Admin | None:
		"""Return the admin only if it has a matching, unexpired session (jti whitelist check)."""
		...


class ProjectRepository(ABC):
	@abstractmethod
	async def list(self, limit: int | None = None) -> list[dto.Project]:
		"""Projects ordered by creation time, oldest first."""
		...

	@abstractmethod
	async def get(self, project_id: uuid.UUID) -> dto.Project | None: ...

	@abstractmethod
	async def create(self, data: dto.ProjectData) -> dto.Project: ...

	@abstractmethod
	async def create_many(self, items: Sequence[dto.ProjectData]) -> None: ...

	@abstractmethod
	async def update(self, project_id: uuid.UUID, changes: Mapping[str, Any]) -> dto.Project | None:
		"""Apply a partial update; returns the fresh row or None if it doesn't exist."""
		...

	@abstractmethod
	async def delete(self, project_id: uuid.UUID) -> bool: ...

	@abstractmethod
	async def has_any(self) -> bool: ...


class LocationRepository(ABC):
	@abstractmethod
	async def get_current(self) -> dto.CurrentLocation | None:
		"""The most recently set location, if any."""
		...

	@abstractmethod
	async def set_current(self, *, location_name: str, latitude: float, longitude: float) -> dto.CurrentLocation: ...

	@abstractmethod
	async def clear(self) -> int:
		"""Remove all stored locations, returning the number of rows removed."""
		...


class BlacklistRepository(ABC):
	@abstractmethod
	async def upsert(self, *, ip_address: str, reason: str, expires_at: datetime) -> None:
		"""Insert or refresh the durable audit record for a blocked IP."""
		...


class Database(ABC):
	"""Facade aggregating the repositories plus connection lifecycle."""

	@property
	@abstractmethod
	def admins(self) -> AdminRepository: ...

	@property
	@abstractmethod
	def projects(self) -> ProjectRepository: ...

	@property
	@abstractmethod
	def locations(self) -> LocationRepository: ...

	@property
	@abstractmethod
	def blacklist(self) -> BlacklistRepository: ...

	@abstractmethod
	async def init(self) -> None:
		"""Create the schema if needed. Called once at application startup."""
		...

	@abstractmethod
	async def close(self) -> None:
		"""Release all connections. Called once at application shutdown."""
		...

	@abstractmethod
	def session(self) -> AbstractAsyncContextManager[None]:
		"""Scope a unit of work: holds a connection for the duration of the block."""
		...

	@abstractmethod
	def transaction(self) -> AbstractAsyncContextManager[None]:
		"""Run the wrapped block atomically."""
		...
