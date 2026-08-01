from datetime import datetime

from pydantic import BaseModel, HttpUrl


class BlogPostSummary(BaseModel):
	slug: str
	title: str
	summary: str
	reading_time_minutes: int
	cover_img: HttpUrl | None = None
	published_at: datetime | None = None


class BlogPostDetail(BlogPostSummary):
	content: str
	meta_title: str | None = None
	meta_description: str | None = None


class BlogPostListResponse(BaseModel):
	items: list[BlogPostSummary]
	total: int
	limit: int
	offset: int
