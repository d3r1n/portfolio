from fastapi import APIRouter, Depends, Response, status

from ..deps import HardcoverDep
from ..integrations.hardcover.schemas import HardcoverBook
from ..schemas.errors import upstream_error_response
from ..security import rate_limit, require_viewer

router = APIRouter(prefix="/books", tags=["Books"], dependencies=[Depends(require_viewer), Depends(rate_limit())])

hardcover_error_response = upstream_error_response(
	"The Hardcover API returned an error", "The upstream hardcover service returned an invalid response"
)


@router.get(
	"/currently-reading",
	response_model=HardcoverBook,
	responses={204: {"description": "No active currently-reading book"}, **hardcover_error_response},
)
async def currently_reading(api: HardcoverDep) -> HardcoverBook | Response:
	book = await api.get_currently_reading_book()
	if book is None:
		return Response(status_code=status.HTTP_204_NO_CONTENT)
	return book
