"""Persistence-layer DTOs.

These are the only types that cross the database facade boundary: repositories
accept and return these, never ORM model instances. Routers/services map them
into API response schemas as needed, so swapping the ORM behind the facade
can't ripple outside the `portfolio.database` package.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class _Record(BaseModel):
	# from_attributes lets implementations hydrate DTOs straight off ORM instances.
	model_config = ConfigDict(from_attributes=True)


class Admin(_Record):
	id: uuid.UUID
	user: str
	email: EmailStr
	hashed_password: str
	created_at: datetime
	updated_at: datetime


class AdminSession(_Record):
	id: uuid.UUID
	admin_id: uuid.UUID
	jti: str
	user_agent: str | None = None
	ip_address: str | None = None
	created_at: datetime
	expires_at: datetime


class Project(_Record):
	id: uuid.UUID
	name: str
	description: str
	year: str | None = None
	status: str | None = None
	tags: list[str] = Field(default_factory=list)
	href: str
	links: list[dict] = Field(default_factory=list)
	accent: str | None = None
	created_at: datetime
	updated_at: datetime


class ProjectData(BaseModel):
	"""Input payload for creating a project (ids/timestamps are the store's job)."""

	name: str = Field(min_length=1, max_length=128)
	description: str = Field(min_length=1, max_length=1024)
	year: str | None = Field(default=None, max_length=8)
	status: str | None = Field(default=None, max_length=32)
	tags: list[str] = Field(default_factory=list)
	href: str = Field(max_length=512)
	links: list[dict] = Field(default_factory=list)
	accent: str | None = Field(default=None, max_length=16)


class CurrentLocation(_Record):
	id: uuid.UUID
	latitude: float = Field(ge=-90, le=90)
	longitude: float = Field(ge=-180, le=180)
	location_name: str
	created_at: datetime
	updated_at: datetime

	@field_validator("location_name", mode="before")
	def _validate_location_name(cls, v) -> str:
		"""Acceptable location names are non-empty comma seperated strings of letters, City/Country format
		e.g. "Istanbul, Turkey" or "New York, USA" or "London, UK"
		"""

		if not v or not isinstance(v, str):
			raise ValueError("Location name must be a non-empty string.")

		parts = [part.strip() for part in v.split(",")]
		if len(parts) != 2 or not all(parts):
			raise ValueError("Location name must be in 'City, Country' format.")

		return v


class BlacklistedIp(_Record):
	id: uuid.UUID
	ip_address: str
	reason: str
	created_at: datetime
	expires_at: datetime
