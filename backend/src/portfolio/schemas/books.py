from pydantic import BaseModel


class HardcoverErrorMessage(BaseModel):
	error: str
	message: str
