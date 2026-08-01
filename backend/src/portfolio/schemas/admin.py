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


class BlogPostRead(BaseModel):
	id: uuid.UUID
	slug: str
	title: str
	summary: str
	content: str
	status: Literal["draft", "published", "archived"]
	reading_time_minutes: int
	meta_title: str | None = None
	meta_description: str | None = None
	cover_img: HttpUrl | None = None
	created_at: datetime
	updated_at: datetime
	published_at: datetime | None = None


class BlogPostCreate(BaseModel):
	title: str = Field(min_length=1, max_length=256)
	summary: str = Field(min_length=1, max_length=512)
	content: str = Field(min_length=1)
	meta_title: str | None = Field(default=None, max_length=70)
	meta_description: str | None = Field(default=None, max_length=160)
	cover_img: HttpUrl | None = None


class BlogPostUpdate(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=256)
	summary: str | None = Field(default=None, min_length=1, max_length=512)
	content: str | None = Field(default=None, min_length=1)
	meta_title: str | None = Field(default=None, max_length=70)
	meta_description: str | None = Field(default=None, max_length=160)
	cover_img: HttpUrl | None = None


class BlogPostStatusUpdate(BaseModel):
	status: Literal["draft", "published", "archived"]


class BlogPostListResponse(BaseModel):
	items: list[BlogPostRead]
	total: int
	limit: int
	offset: int
