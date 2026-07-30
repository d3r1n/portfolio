import pytest
from fastapi import HTTPException

from portfolio.security.jwt import (
	create_admin_token,
	create_viewer_token,
	verify_viewer_token,
)


def test_viewer_token_roundtrip():
	verify_viewer_token(create_viewer_token())  # must not raise


def test_viewer_token_rejects_garbage():
	with pytest.raises(HTTPException) as exc_info:
		verify_viewer_token("not-a-jwt")
	assert exc_info.value.status_code == 401


def test_viewer_token_rejects_admin_role():
	token, _ = create_admin_token("00000000-0000-0000-0000-000000000000")
	with pytest.raises(HTTPException) as exc_info:
		verify_viewer_token(token)
	assert exc_info.value.status_code == 403


def test_admin_token_payload():
	token, payload = create_admin_token("some-admin-id")
	assert token
	assert payload["sub"] == "some-admin-id"
	assert payload["role"] == "admin"
	assert payload["jti"]
	assert payload["exp"] > 0
