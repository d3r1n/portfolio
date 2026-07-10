import uuid
from datetime import datetime, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status
from loguru import logger
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_async_session
from ..util.config import load_config
from .models import Admin, AdminSession

config = load_config()


JWT_SECRET_KEY = config.security.jwt_secret_key
JWT_ALGORITHM = config.security.jwt_algorithm


def get_client_ip(request: Request) -> str:
	"""
	Safely extracts the real client IP address, accounting for the
	upstream reverse proxy layer (Caddy).
	"""
	# Check the standard header Caddy sets for the original client
	real_ip = request.headers.get("X-Real-IP")
	if real_ip:
		return real_ip

	# Fall back to X-Forwarded-For (can be a comma-separated list: client, proxy1, proxy2)
	forwarded_for = request.headers.get("X-Forwarded-For")
	if forwarded_for:
		# Grab the very first IP in the chain, which is the original client
		return forwarded_for.split(",")[0].strip()

	# local fallback if things aren't hitting the proxy during testing
	return request.client.host if request.client else "127.0.0.1"


async def require_admin(
	request: Request,  # Pull raw request context to inspect headers and cookies manually
	session: AsyncSession = Depends(get_async_session),
) -> Admin:
	"""
	Reusable dependency to protect administrative operations.
	Validates signature, role permissions, and user state in Postgres.
	Extracts authorization payload seamlessly from headers or browser cookies.
	"""
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate administrative credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	token = None

	# 1. Look for Authorization Header first (used by normal frontend fetch/axios calls)
	auth_header = request.headers.get("Authorization")
	if auth_header and auth_header.startswith("Bearer "):
		token = auth_header.split(" ")[1]

	# 2. Fall back to Cookie parsing if the header isn't there (used during direct Caddy page redirects)
	if not token:
		token = request.cookies.get("admin_token")
		logger.debug(f"Cookies: {request.cookies}")

	# If neither strategy yields an extraction target, drop out immediately
	if not token:
		raise credentials_exception

	try:
		payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
		admin_id: str | None = payload.get("sub")
		role: str | None = payload.get("role")
		jti: str | None = payload.get("jti")  # Grab the whitelist tracking ID

		if not admin_id or role != "admin" or not jti:
			raise credentials_exception

		admin_uuid = uuid.UUID(admin_id)

	except (jwt.InvalidTokenError, ValueError):
		raise credentials_exception

	# Enforce the whitelist join query:
	# Look for the admin, but ONLY if they have a matching, unexpired record in admin_sessions
	statement = (
		select(Admin)
		.join(AdminSession, Admin.id == AdminSession.admin_id)  # pyright: ignore[reportArgumentType]
		.where(Admin.id == admin_uuid)
		.where(AdminSession.jti == jti)
		.where(AdminSession.expires_at > datetime.now(timezone.utc))
	)
	result = await session.exec(statement)
	admin = result.one_or_none()

	if admin is None:
		raise credentials_exception

	return admin
