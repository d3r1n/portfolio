from pydantic import BaseModel, Field, HttpUrl


class ProjectLink(BaseModel):
	label: str
	href: HttpUrl
	external: bool = True


class FeaturedProject(BaseModel):
	name: str
	description: str
	year: str | None = None
	status: str | None = None
	tags: list[str] = Field(default_factory=list)
	href: HttpUrl
	links: list[ProjectLink] = Field(default_factory=list)
	accent: str | None = None
