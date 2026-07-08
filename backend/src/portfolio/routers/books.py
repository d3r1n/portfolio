from typing import Annotated

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from portfolio.lib.security import require_viewer

from ..deps import get_client_session, get_hardcover_api
from ..lib.api.hardcover_api import HardcoverApi, HardcoverBook, HardcoverError

router = APIRouter(prefix="/books", tags=["Books"], dependencies=[Depends(require_viewer)])


class HardcoverErrorMessage(BaseModel):
	error: str
	message: str


hardcover_error_response = {
	502: {
		"model": HardcoverErrorMessage,
		"description": "The Hardcover API returned an error",
		"content": {
			"application/json": {
				"example": {
					"error": "HardcoverError",
					"message": "The upstream hardcover service returned an invalid response",
				},
			},
		},
	},
}


def _hardcover_error_message(error: HardcoverError) -> str:
	if not error.args:
		return "Unknown hardcover service error"
	detail = error.args[0]
	if isinstance(detail, dict):
		message = detail.get("message")
		if isinstance(message, str):
			return message
	return "Unknown hardcover service error"


@router.get(
	"/currently-reading",
	response_model=HardcoverBook,
	responses={204: {"description": "No active currently-reading book"}, **hardcover_error_response},
)
async def currently_reading(
	api: Annotated[HardcoverApi, Depends(get_hardcover_api)],
	session: Annotated[ClientSession, Depends(get_client_session)],
) -> HardcoverBook | Response:
	try:
		book = await api.get_currently_reading_book(session)

		if book is None:
			return Response(status_code=status.HTTP_204_NO_CONTENT)

		return book
	except HardcoverError as e:
		error_msg = _hardcover_error_message(e)
		logger.error(f"Hardcover tracking error mapped to 502: {error_msg}")
		return JSONResponse(
			status_code=status.HTTP_502_BAD_GATEWAY,
			content={"error": "HardcoverError", "message": error_msg},
		)
