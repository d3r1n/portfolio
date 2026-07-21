from pydantic import BaseModel, Field, HttpUrl


class Track(BaseModel):
	"""Dataclass representing the a track returned from the spotify api.

	Most of the data from the original response isn't included here since
	we're only interested in data our application actually requires.
	"""

	name: str
	artists: list[str]
	track_url: HttpUrl
	is_playing: bool | None = Field(default=None)
	album_name: str
	album_image: HttpUrl
	duration_ms: int | None = Field(default=None)
	progress_ms: int | None = Field(default=None)


class TopArtist(BaseModel):
	"""Dataclass representing an artist returned from the spotify's top artists response."""

	name: str
	url: HttpUrl
	image: HttpUrl
