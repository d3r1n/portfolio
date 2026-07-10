import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, TypedDict, cast

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer

from ..util.config import load_config

config = load_config()

JWT_SECRET_KEY = config.security.jwt_secret_key
JWT_ALGORITHM = config.security.jwt_algorithm
JWT_VIEWER_TOKEN_EXPIRE_MINUTES = config.security.jwt_viewer_token_expire_minutes
JWT_ADMIN_TOKEN_EXPIRE_MINUTES = config.security.jwt_admin_token_expire_minutes


# We use HTTPBearer to automatically extract the 'Authorization: Bearer <token>' header
# auto_error=False ensures we can handle missing tokens manually with descriptive messages
viewer_bearer = HTTPBearer(auto_error=False)


class ViewerPayload(TypedDict):
	role: Literal["viewer"]
	exp: int


def create_viewer_token() -> str:
	"""Generates a cryptographically signed, short-lived viewer JWT."""
	expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_VIEWER_TOKEN_EXPIRE_MINUTES)

	payload: ViewerPayload = {"role": "viewer", "exp": int(expire.timestamp())}

	# Sign the token using your secret key and HS256 algorithm
	return jwt.encode(cast(dict[str, Any], payload), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_viewer_token(token: str) -> None:
	"""Decodes and validates a viewer JWT without hitting the database."""
	try:
		payload = jwt.decode(token, config.security.jwt_secret_key, algorithms=[config.security.jwt_algorithm])

		# Enforce that this token belongs explicitly to a viewer
		if payload.get("role") != "viewer":
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token role profile")

	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Viewer session has expired")
	except jwt.InvalidTokenError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid viewer credentials")


def require_viewer(credentials: HTTPAuthorizationCredentials | None = Depends(viewer_bearer)) -> None:
	"""
	FastAPI Dependency to safeguard endpoints.
	Verifies signature and expiration instantly. No database hits.
	"""
	if credentials is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing viewer authentication credentials"
		)

	# credentials.credentials contains the raw JWT string extracted by HTTPBearer
	verify_viewer_token(credentials.credentials)


# We use the native OAuth2PasswordBearer flow for the admin dashboard.
# This instructs FastAPI to read form data and configures the login UI in /docs.
admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/admin-login")


class AdminPayload(TypedDict):
	sub: str  # The Admin's unique string UUID
	role: Literal["admin"]
	jti: str  # Unique JWT ID for session tracking
	exp: int


def create_admin_token(admin_id: str) -> tuple[str, AdminPayload]:
	"""Generates an administrative access token with high-privilege claims."""

	jti = secrets.token_hex(16)  # Unique JWT ID for session tracking
	expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ADMIN_TOKEN_EXPIRE_MINUTES)

	payload: AdminPayload = {"sub": admin_id, "role": "admin", "jti": jti, "exp": int(expire.timestamp())}

	return (
		jwt.encode(cast(dict[str, Any], payload), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
		payload,
	)
