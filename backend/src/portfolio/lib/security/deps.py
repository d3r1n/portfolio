from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt import verify_viewer_token

# We use HTTPBearer to automatically extract the 'Authorization: Bearer <token>' header
# auto_error=False ensures we can handle missing tokens manually with descriptive messages
viewer_bearer = HTTPBearer(auto_error=False)


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
