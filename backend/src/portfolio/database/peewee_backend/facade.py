"""Peewee-backed implementation of the `Database` facade."""

from contextlib import AbstractAsyncContextManager, asynccontextmanager

from loguru import logger
from playhouse.pwasyncio import AsyncDatabaseMixin

from ..interface import Database
from . import models
from .repositories import (
	PeeweeAdminRepository,
	PeeweeBlacklistRepository,
	PeeweeLocationRepository,
	PeeweeProjectRepository,
)


class PeeweeDatabase(Database):
	def __init__(self, db: AsyncDatabaseMixin | None = None):
		# `db` is injectable so tests can run the same facade against e.g. an
		# in-memory AsyncSqliteDatabase (with the models bound via bind_ctx).
		self._db = db if db is not None else models.database
		self._admins = PeeweeAdminRepository(self._db)
		self._projects = PeeweeProjectRepository(self._db)
		self._locations = PeeweeLocationRepository(self._db)
		self._blacklist = PeeweeBlacklistRepository(self._db)

	@property
	def admins(self) -> PeeweeAdminRepository:
		return self._admins

	@property
	def projects(self) -> PeeweeProjectRepository:
		return self._projects

	@property
	def locations(self) -> PeeweeLocationRepository:
		return self._locations

	@property
	def blacklist(self) -> PeeweeBlacklistRepository:
		return self._blacklist

	async def init(self) -> None:
		async with self._db:
			# Creates tables (and indexes/constraints) that do not exist yet.
			await self._db.acreate_tables(models.ALL_MODELS)
		logger.info("Database initialized successfully.")

	async def close(self) -> None:
		await self._db.close_pool()

	@asynccontextmanager
	async def _session(self):
		# pwasyncio connections are task-local; entering acquires a pooled
		# connection for the current task, exiting releases it. Nested entry is
		# safe: aconnect() reuses the connection already held by the task.
		async with self._db:
			yield

	def session(self) -> AbstractAsyncContextManager[None]:
		return self._session()

	@asynccontextmanager
	async def _transaction(self):
		async with self._db.atomic():
			yield

	def transaction(self) -> AbstractAsyncContextManager[None]:
		return self._transaction()
