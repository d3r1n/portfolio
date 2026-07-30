import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from .projects import FeaturedProject, ProjectLink


class StatusMessage(BaseModel):
	"""Generic status/message envelope for admin dashboard success and error responses."""

	status: Literal["success", "error"]
	message: str


class ProjectRead(FeaturedProject):
	id: uuid.UUID
	created_at: datetime
	updated_at: datetime


class ProjectCreate(BaseModel):
	name: str = Field(min_length=1, max_length=128)
	description: str = Field(min_length=1, max_length=1024)
	year: str | None = Field(default=None, max_length=8)
	status: str | None = Field(default=None, max_length=32)
	tags: list[str] = Field(default_factory=list)
	href: HttpUrl
	links: list[ProjectLink] = Field(default_factory=list)
	accent: str | None = Field(default=None, max_length=16)


class ProjectUpdate(BaseModel):
	name: str | None = Field(default=None, min_length=1, max_length=128)
	description: str | None = Field(default=None, min_length=1, max_length=1024)
	year: str | None = Field(default=None, max_length=8)
	status: str | None = Field(default=None, max_length=32)
	tags: list[str] | None = None
	href: HttpUrl | None = None
	links: list[ProjectLink] | None = None
	accent: str | None = Field(default=None, max_length=16)
