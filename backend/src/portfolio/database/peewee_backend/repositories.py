"""Peewee implementations of the repository interfaces.

Each method executes through peewee 4.x's asyncio bridge (`playhouse.pwasyncio`)
and hydrates DTOs before returning, so no peewee instance escapes this module.
"""

import uuid
from datetime import datetime
from typing import Any, Mapping, Sequence

from playhouse.pwasyncio import AsyncDatabaseMixin

from .. import dto
from ..interface import AdminRepository, BlacklistRepository, LocationRepository, ProjectRepository
from . import models


class PeeweeAdminRepository(AdminRepository):
	def __init__(self, db: AsyncDatabaseMixin):
		self._db = db

	async def get_by_username(self, username: str) -> dto.Admin | None:
		row = await models.Admin.aget_or_none(models.Admin.user == username)
		return dto.Admin.model_validate(row) if row else None

	async def create(self, *, user: str, email: str, hashed_password: str) -> dto.Admin:
		row = await models.Admin.acreate(user=user, email=email, hashed_password=hashed_password)
		return dto.Admin.model_validate(row)

	async def create_session(
		self,
		*,
		admin_id: uuid.UUID,
		jti: str,
		expires_at: datetime,
		user_agent: str | None = None,
		ip_address: str | None = None,
	) -> dto.AdminSession:
		row = await models.AdminSession.acreate(
			admin=admin_id, jti=jti, expires_at=expires_at, user_agent=user_agent, ip_address=ip_address
		)
		return dto.AdminSession.model_validate(row)

	async def get_by_valid_session(self, admin_id: uuid.UUID, jti: str) -> dto.Admin | None:
		# The whitelist join: the admin only authenticates while a matching,
		# unexpired session row exists for the token's jti.
		query = (
			models.Admin.select()
			.join(models.AdminSession, on=(models.AdminSession.admin == models.Admin.id))
			.where(
				(models.Admin.id == admin_id)
				& (models.AdminSession.jti == jti)
				& (models.AdminSession.expires_at > models.utcnow())
			)
		)
		row = await self._db.first(query)
		return dto.Admin.model_validate(row) if row else None


class PeeweeProjectRepository(ProjectRepository):
	def __init__(self, db: AsyncDatabaseMixin):
		self._db = db

	async def list(self, limit: int | None = None) -> list[dto.Project]:
		query = models.Project.select().order_by(models.Project.created_at)
		if limit is not None:
			query = query.limit(limit)
		return [dto.Project.model_validate(row) for row in await query.aexecute()]

	async def get(self, project_id: uuid.UUID) -> dto.Project | None:
		row = await models.Project.aget_or_none(models.Project.id == project_id)
		return dto.Project.model_validate(row) if row else None

	async def create(self, data: dto.ProjectData) -> dto.Project:
		row = await models.Project.acreate(**data.model_dump())
		return dto.Project.model_validate(row)

	async def create_many(self, items: Sequence[dto.ProjectData]) -> None:
		if items:
			await models.Project.insert_many([item.model_dump() for item in items]).aexecute()

	async def update(self, project_id: uuid.UUID, changes: Mapping[str, Any]) -> dto.Project | None:
		# updated_at is maintained here (the SQLAlchemy `onupdate` hook equivalent).
		modified = await (
			models.Project.update(**changes, updated_at=models.utcnow())
			.where(models.Project.id == project_id)
			.aexecute()
		)
		if not modified:
			return None
		return await self.get(project_id)

	async def delete(self, project_id: uuid.UUID) -> bool:
		return bool(await models.Project.delete().where(models.Project.id == project_id).aexecute())

	async def has_any(self) -> bool:
		return bool(await self._db.exists(models.Project.select()))


class PeeweeLocationRepository(LocationRepository):
	def __init__(self, db: AsyncDatabaseMixin):
		self._db = db

	async def get_current(self) -> dto.CurrentLocation | None:
		query = models.CurrentLocation.select().order_by(models.CurrentLocation.created_at.desc())
		row = await self._db.first(query)
		return dto.CurrentLocation.model_validate(row) if row else None

	async def set_current(self, *, location_name: str, latitude: float, longitude: float) -> dto.CurrentLocation:
		row = await models.CurrentLocation.acreate(location_name=location_name, latitude=latitude, longitude=longitude)
		return dto.CurrentLocation.model_validate(row)

	async def clear(self) -> int:
		return await models.CurrentLocation.delete().aexecute()


class PeeweeBlacklistRepository(BlacklistRepository):
	def __init__(self, db: AsyncDatabaseMixin):
		self._db = db

	async def upsert(self, *, ip_address: str, reason: str, expires_at: datetime) -> None:
		await (
			models.BlacklistedIp.insert(ip_address=ip_address, reason=reason, expires_at=expires_at)
			.on_conflict(
				conflict_target=[models.BlacklistedIp.ip_address],
				update={
					models.BlacklistedIp.reason: reason,
					models.BlacklistedIp.expires_at: expires_at,
				},
			)
			.aexecute()
		)
