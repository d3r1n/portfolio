from typing import Annotated

from aiohttp import ClientSession
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response

from python_backend.dependencies import get_client_session
from python_backend.lib.hardcover_api import HardcoverApi, HardcoverBook

router = APIRouter(prefix="/books")

_hardcover_api = HardcoverApi()


@router.get("/currently-reading")
async def currently_reading(
	session: Annotated[ClientSession, Depends(get_client_session)],
) -> HardcoverBook | None:
	book = await _hardcover_api.get_currently_reading_book(session)

	if not book:
		return Response(status_code=204)

	return JSONResponse(content=book, status_code=200)
