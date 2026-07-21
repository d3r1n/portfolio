from pydantic import BaseModel


class SpotifyErrorMessage(BaseModel):
	error: str
	message: str
