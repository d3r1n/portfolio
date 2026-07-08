from fastapi import APIRouter
from pydantic import BaseModel

from ..lib.security import create_viewer_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"


@router.post("/viewer-session", response_model=TokenResponse)
async def generate_viewer_session() -> TokenResponse:
	"""
	Endpoint called by the frontend on the visitor's first initial page load.
	Returns a signed, stateless token valid for 30 minutes.
	"""
	token = create_viewer_token()
	return TokenResponse(access_token=token)
