from datetime import datetime, timedelta, timezone
from typing import Any, Literal, TypedDict, cast

import jwt
from fastapi import HTTPException, status

from ...deps import get_config

config = get_config()


class ViewerPayload(TypedDict):
	role: Literal["viewer"]
	exp: int


def create_viewer_token() -> str:
	"""Generates a cryptographically signed, short-lived viewer JWT."""
	expire = datetime.now(timezone.utc) + timedelta(minutes=config.security.jwt_viewer_token_expire_minutes)

	payload: ViewerPayload = {"role": "viewer", "exp": int(expire.timestamp())}

	# Sign the token using your secret key and HS256 algorithm
	return jwt.encode(
		cast(dict[str, Any], payload), config.security.jwt_secret_key, algorithm=config.security.jwt_algorithm
	)


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
