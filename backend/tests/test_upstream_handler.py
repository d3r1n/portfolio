"""The app-level UpstreamError handler maps any integration failure to one 502 shape."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from portfolio.integrations.spotify.client import SpotifyError
from portfolio.main import upstream_error_handler


def test_upstream_error_becomes_502():
	app = FastAPI()
	app.add_exception_handler(SpotifyError, upstream_error_handler)  # pyright: ignore[reportArgumentType]

	@app.get("/boom")
	async def boom():
		raise SpotifyError("token refresh failed", status_code=401)

	client = TestClient(app, raise_server_exceptions=False)
	response = client.get("/boom")

	assert response.status_code == 502
	assert response.json() == {"error": "SpotifyError", "message": "token refresh failed"}
