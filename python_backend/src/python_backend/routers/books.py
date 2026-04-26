from typing import Annotated

from aiohttp import ClientSession
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response

from ..deps import get_hardcover_service
from ..lib.api.hardcover_api import HardcoverApi, HardcoverBook, HardcoverError

router = APIRouter(prefix="/books")


@router.get("/currently-reading")
async def currently_reading(
	service: Annotated[tuple[HardcoverApi, ClientSession], Depends(get_hardcover_service)],
) -> HardcoverBook | None:
	api, session = service

	if api and session:
		try:
			book = await api.get_currently_reading_book(session)

			if not book:
				return Response(status_code=204)

			return JSONResponse(content=book, status_code=200)
		except HardcoverError as e:
			return JSONResponse(
				{"error": "HardcoverError", "message": e.args[0]["message"]},
				status_code=502,
			)
