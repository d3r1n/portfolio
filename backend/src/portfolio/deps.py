from functools import lru_cache
from typing import Annotated

from aiohttp import ClientSession
from fastapi import Depends

from .lib.api.hardcover_api import HardcoverApi
from .lib.api.spotify_api import SpotifyApi
from .lib.util.config import Config, load_config


# Config Management
@lru_cache
def get_config() -> Config:
	return load_config()


# Session Management
class ClientSessionManager:
	def __init__(self):
		self._session: ClientSession | None = None

	def __call__(self) -> ClientSession:
		if self._session is None:
			raise RuntimeError("ClientSession not initialized. Ensure lifespan is set in main.py")
		return self._session

	async def init(self) -> None:
		if self._session is None:
			self._session = ClientSession()

	async def close(self) -> None:
		if self._session:
			await self._session.close()
			self._session = None


get_client_session = ClientSessionManager()


@lru_cache
def _get_spotify_api() -> SpotifyApi:
	"""Singleton provider for SpotifyApi."""
	config = get_config()
	return SpotifyApi(config)


@lru_cache
def get_hardcover_api() -> HardcoverApi:
	"""Singleton provider for HardcoverApi."""
	config = get_config()
	return HardcoverApi(config)


type SpotifyService = tuple[SpotifyApi, ClientSession]
type HardcoverService = tuple[HardcoverApi, ClientSession]


async def get_spotify_service(
	api: Annotated[SpotifyApi, Depends(_get_spotify_api)],
	session: Annotated[ClientSession, Depends(get_client_session)],
) -> SpotifyService:
	return api, session


async def get_hardcover_service(
	api: Annotated[HardcoverApi, Depends(get_hardcover_api)],
	session: Annotated[ClientSession, Depends(get_client_session)],
) -> HardcoverService:
	return api, session
