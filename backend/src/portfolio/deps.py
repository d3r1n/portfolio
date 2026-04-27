from functools import lru_cache
from os import environ
from typing import Annotated, Literal

from aiohttp import ClientSession
from fastapi import Depends

from .lib.api.hardcover_api import HardcoverApi
from .lib.api.spotify_api import SpotifyApi
from .lib.util.config import Config, load_config


# Config Management
@lru_cache
def get_config() -> Config:
	"""
	Handles DEPLOYMENT_MODE safely.
	Converts to uppercase to handle 'dev' vs 'DEV'.
	"""
	mode = environ.get("DEPLOYMENT_MODE", "DEV").upper()

	if mode not in ["DEV", "PROD"]:
		mode = "DEV"

	return load_config(mode)  # type: ignore


# Session Management
class ClientSessionManager:
	def __init__(self):
		self._session: ClientSession | None = None

	def __call__(self) -> ClientSession:
		if self._session is None:
			raise RuntimeError("ClientSession not initialized. Ensure lifespan is set in main.py")
		return self._session

	async def init(self):
		if self._session is None:
			self._session = ClientSession()

	async def close(self):
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
def _get_hardcover_api() -> HardcoverApi:
	"""Singleton provider for HardcoverApi."""
	config = get_config()
	return HardcoverApi(config)


async def get_spotify_service(
	api: Annotated[SpotifyApi, Depends(_get_spotify_api)],
	session: Annotated[ClientSession, Depends(get_client_session)],
):
	return api, session


async def get_hardcover_service(
	api: Annotated[HardcoverApi, Depends(_get_hardcover_api)],
	session: Annotated[ClientSession, Depends(get_client_session)],
):
	return api, session
