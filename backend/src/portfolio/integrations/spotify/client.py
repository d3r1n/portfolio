import base64
from datetime import datetime, timedelta
from typing import Any

from aiohttp import ClientSession
from loguru import logger

from ...core.config import Config
from .. import UpstreamError
from .schemas import TopArtist, Track


class SpotifyError(UpstreamError):
	service = "Spotify"


def _open_spotify_url(kind: str, uri: str) -> str:
	# Spotify URIs look like "spotify:track:<id>"; the web URL wants just the id.
	return f"https://open.spotify.com/{kind}/{uri.split(':')[2]}"


def _parse_track(item: dict[str, Any], **extra: Any) -> Track:
	"""Build a Track from a Spotify track object (shared by all track endpoints)."""
	return Track(
		name=item["name"],
		album_name=item["album"]["name"],
		album_image=item["album"]["images"][0]["url"],
		artists=[artist.get("name", "Unknown Artist") for artist in item["artists"]],
		track_url=_open_spotify_url("track", item["uri"]),
		**extra,
	)


class SpotifyApi:
	"""Client for the Spotify Web API, bound to the app-wide aiohttp session.

	Handles access-token refresh transparently; exposes currently-playing,
	last-played and monthly-top queries.
	"""

	BASE_URL = "https://api.spotify.com/v1"
	AUTH_URL = "https://accounts.spotify.com/api"

	def __init__(self, config: Config, session: ClientSession) -> None:
		self._session = session
		self._client_id = config.spotify.client_id
		self._client_secret = config.spotify.client_secret
		self._refresh_token = config.spotify.refresh_token

		self._access_token: str | None = None
		self._expiry_time: datetime | None = None

	async def _refresh_access_token(self) -> None:
		"""Fetch a new access token, unless the cached one is still valid."""
		if self._expiry_time and datetime.now() <= self._expiry_time:
			return

		basic_auth = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode("utf-8")

		response = await self._session.post(
			f"{self.AUTH_URL}/token",
			headers={"Authorization": f"Basic {basic_auth}"},
			data={"grant_type": "refresh_token", "refresh_token": self._refresh_token},
		)

		if response.status != 200:
			raise SpotifyError(await response.text(), status_code=response.status)

		data = await response.json()
		self._access_token = data["access_token"]
		self._expiry_time = datetime.now() + timedelta(seconds=data["expires_in"])

	async def _get(self, path: str, **params: Any) -> dict[str, Any] | None:
		"""GET an API path with a fresh token. Returns None on 204 (no content)."""
		await self._refresh_access_token()

		response = await self._session.get(
			f"{self.BASE_URL}{path}",
			params=params or None,
			headers={"Authorization": f"Bearer {self._access_token}"},
		)

		if response.status == 204:
			return None
		if response.status != 200:
			raise SpotifyError(await response.text(), status_code=response.status)

		return await response.json()

	async def get_currently_playing(self) -> Track | None:
		"""The user's currently playing track, or None if nothing is playing."""
		data = await self._get("/me/player/currently-playing")
		if data is None:
			return None

		logger.debug(f"Currently playing track data: {data}")
		item = data["item"]
		return _parse_track(
			item,
			is_playing=data["is_playing"],
			progress_ms=data["progress_ms"],
			duration_ms=item["duration_ms"],
		)

	async def get_last_played_track(self) -> Track | None:
		"""The user's most recently played track, or None if there is none."""
		data = await self._get("/me/player/recently-played", limit=1)
		if data is None:
			return None

		logger.debug(f"Last played track data: {data}")
		return _parse_track(data["items"][0]["track"])

	async def get_top_month_tracks(self, limit: int = 10) -> list[Track] | None:
		"""The user's top tracks of the last 4 weeks."""
		data = await self._get("/me/top/tracks", limit=limit, time_range="short_term")
		if data is None:
			return None

		return [_parse_track(item) for item in data["items"]]

	async def get_top_month_artists(self, limit: int = 10) -> list[TopArtist] | None:
		"""The user's top artists of the last 4 weeks."""
		data = await self._get("/me/top/artists", limit=limit, time_range="short_term")
		if data is None:
			return None

		return [
			TopArtist(
				name=item["name"],
				url=_open_spotify_url("artist", item["uri"]),
				image=item["images"][0]["url"],
			)
			for item in data["items"]
		]
