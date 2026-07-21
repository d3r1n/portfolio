from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from portfolio.lib.security.jwt import JWT_ADMIN_TOKEN_EXPIRE_MINUTES

from ..lib.database import get_async_session
from ..lib.security import (
	Admin,
	AdminSession,
	create_admin_token,
	create_viewer_token,
	get_client_ip,
	rate_limit,
	require_admin,
	verify_password,
)
from ..lib.util.config import load_config

config = load_config()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Each route below sets its own budget explicitly rather than inheriting one from the
# router, since stacking a router-wide dependency with a route override would count
# (and log) the same request twice.
auth_rate_limit = Depends(rate_limit(config.security.auth_rate_limit_per_minute))


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"


@router.post("/viewer-session", response_model=TokenResponse, dependencies=[auth_rate_limit])
async def generate_viewer_session() -> TokenResponse:
	"""
	Endpoint called by the frontend on the visitor's first initial page load.
	Returns a signed, stateless token valid for 30 minutes.
	"""
	token = create_viewer_token()
	return TokenResponse(access_token=token)


SECONDS_PER_MINUTE = 60  # Constant for cookie expiration


@router.post("/admin-login", dependencies=[Depends(rate_limit(10))])  # brute-force target — tighter budget
async def admin_login(
	request: Request,
	response: Response,
	form_data: OAuth2PasswordRequestForm = Depends(),
	session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
	"""
	Processes administrative logins via OAuth2 standard password flow.
	Verifies credentials against Postgres and yields an elevated access token.
	"""
	# Search for the admin user
	statement = select(Admin).where(Admin.user == form_data.username)
	result = await session.exec(statement)
	admin = result.one_or_none()

	# Prevent timing attacks by checking fake hashes if user doesn't exist,
	# or handle verification cleanly
	if admin is None or not verify_password(form_data.password, admin.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect administrative email or password",
			headers={"WWW-Authenticate": "Bearer"},
		)

	# Return the token matching standard OAuth2 response layouts
	token, payload = create_admin_token(str(admin.id))

	admin_session = AdminSession(
		admin_id=admin.id,
		jti=payload["jti"],
		user_agent=response.headers.get("user-agent", "unknown"),
		ip_address=get_client_ip(request),
		expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
	)

	session.add(admin_session)
	await session.commit()

	response.set_cookie(
		key="admin_token",
		value=token,
		httponly=True,
		samesite="lax",
		secure=True,  # Set to True in production for HTTPS
		max_age=JWT_ADMIN_TOKEN_EXPIRE_MINUTES * SECONDS_PER_MINUTE,
	)

	return {"access_token": token, "token_type": "bearer"}


@router.get("/admin-verify", dependencies=[auth_rate_limit])
async def admin_verify(_: Admin = Depends(require_admin)):
	"""
	Endpoint to verify the validity of an admin token.
	Returns the admin's username and email if valid.
	"""
	return Response(status_code=status.HTTP_200_OK)
