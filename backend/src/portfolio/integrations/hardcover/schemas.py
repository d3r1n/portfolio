from pydantic import BaseModel, HttpUrl


class HardcoverBook(BaseModel):
	title: str
	author: str
	pages: int | None = None
	image_url: HttpUrl | None = None
	image_dominant_color: str | None = None
	progress: float | None = None
	link: HttpUrl
