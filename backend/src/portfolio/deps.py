from functools import lru_cache
from typing import Annotated

from aiohttp import ClientSession
from fastapi import Depends
from redis.asyncio import Redis

from .core.config import Config, load_config
from .integrations.hardcover.client import HardcoverApi
from .integrations.spotify.client import SpotifyApi


# Config Management
def get_config() -> Config:
	# load_config() is itself cached, so this is just a Depends()-friendly alias.
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


# Redis connection (rate limiter's hot path — counters and the live blacklist cache).
# Unlike aiohttp's ClientSession, redis.asyncio.Redis connects lazily on first command
# and doesn't need a running event loop to construct, so a plain lru_cache singleton
# (same pattern as the API clients below) is enough — no init/close state machine needed.
@lru_cache
def get_redis() -> Redis:
	return Redis.from_url(load_config().redis_url, decode_responses=True)


@lru_cache
def _get_spotify_api() -> SpotifyApi:
	"""Singleton provider for SpotifyApi."""
	config = get_config()
	return SpotifyApi(config)


@lru_cache
def _get_hardcover_api() -> HardcoverApi:
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
	api: Annotated[HardcoverApi, Depends(_get_hardcover_api)],
	session: Annotated[ClientSession, Depends(get_client_session)],
) -> HardcoverService:
	return api, session
