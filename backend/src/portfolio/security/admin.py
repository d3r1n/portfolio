import uuid

import jwt
from fastapi import Depends, HTTPException, Request, status
from loguru import logger

from ..core.config import load_config
from ..database import Database, get_db
from ..database.dto import Admin

config = load_config()


JWT_SECRET_KEY = config.security.jwt_secret_key
JWT_ALGORITHM = config.security.jwt_algorithm


async def require_admin(
	request: Request,  # Pull raw request context to inspect headers and cookies manually
	db: Database = Depends(get_db),
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

	# Enforce the whitelist check: the admin resolves only while a matching,
	# unexpired record exists in admin_sessions
	admin = await db.admins.get_by_valid_session(admin_uuid, jti)

	if admin is None:
		raise credentials_exception

	return admin
