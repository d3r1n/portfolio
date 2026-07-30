"""Peewee model definitions — private to the peewee backend.

Nothing outside `portfolio.database.peewee_backend` may import these; callers
go through the `Database` facade and only ever see the DTOs in `database.dto`.
"""

import uuid
from datetime import datetime, timezone

from peewee import CharField, FloatField, ForeignKeyField, JSONField, TextField, UUIDField
from playhouse.postgres_ext import DateTimeTZField
from playhouse.pwasyncio import AsyncModel, AsyncPostgresqlDatabase

from ...core.config import load_config


def _normalize_db_url(url: str) -> str:
	"""Accept SQLAlchemy-style URLs ("postgresql+asyncpg://...") by dropping the
	driver suffix — asyncpg is the only driver here, so it carries no information."""
	scheme, sep, rest = url.partition("://")
	return scheme.split("+", 1)[0] + sep + rest


def utcnow() -> datetime:
	return datetime.now(timezone.utc)


database = AsyncPostgresqlDatabase(_normalize_db_url(load_config().db_url))


class BaseModel(AsyncModel):
	class Meta:
		database = database
		legacy_table_names = False  # peewee 3.0+ uses class name as table name by default


class Admin(BaseModel):
	class Meta:
		table_name = "admins"

	id = UUIDField(primary_key=True, default=uuid.uuid4)

	user = CharField(max_length=64)
	email = CharField(max_length=255, unique=True, index=True)
	hashed_password = TextField()

	# We enforce UTC timezone at the application level; TIMESTAMPTZ keeps
	# asyncpg happy with the tz-aware datetimes used throughout the app.
	created_at = DateTimeTZField(default=utcnow)
	updated_at = DateTimeTZField(default=utcnow)


class AdminSession(BaseModel):
	class Meta:
		table_name = "admin_sessions"

	id = UUIDField(primary_key=True, default=uuid.uuid4)

	# lazy_load=False: attribute access yields the raw admin id instead of
	# triggering an implicit query (which would raise MissingGreenletBridge
	# outside the async bridge anyway). Reads that need the admin join explicitly.
	admin = ForeignKeyField(Admin, backref="sessions", column_name="admin_id", on_delete="CASCADE", lazy_load=False)

	# Store the unique JWT ID token identifier
	jti = CharField(unique=True, index=True)

	# Track metadata for security auditing
	user_agent = TextField(null=True)
	ip_address = TextField(null=True)

	created_at = DateTimeTZField(default=utcnow)
	expires_at = DateTimeTZField()


class Project(BaseModel):
	class Meta:
		table_name = "project"

	id = UUIDField(primary_key=True, default=uuid.uuid4)

	name = CharField(max_length=128)
	description = CharField(max_length=1024)
	year = CharField(max_length=8, null=True)
	status = CharField(max_length=32, null=True)
	tags = JSONField(default=list)
	href = CharField(max_length=512)
	links = JSONField(default=list)
	accent = CharField(max_length=16, null=True)

	created_at = DateTimeTZField(default=utcnow)
	updated_at = DateTimeTZField(default=utcnow)


class CurrentLocation(BaseModel):
	class Meta:
		table_name = "current_location"

	id = UUIDField(primary_key=True, default=uuid.uuid4)

	latitude = FloatField()
	longitude = FloatField()
	location_name = CharField(max_length=128)

	created_at = DateTimeTZField(default=utcnow)
	updated_at = DateTimeTZField(default=utcnow)


class BlacklistedIp(BaseModel):
	class Meta:
		table_name = "blacklisted_ips"

	id = UUIDField(primary_key=True, default=uuid.uuid4)

	ip_address = CharField(max_length=64, unique=True, index=True)
	reason = TextField()

	created_at = DateTimeTZField(default=utcnow)
	expires_at = DateTimeTZField(index=True)


ALL_MODELS = [Admin, AdminSession, Project, CurrentLocation, BlacklistedIp]
