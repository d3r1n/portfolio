from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from .core.config import Config, load_config
from .integrations.hardcover.client import HardcoverApi
from .integrations.openweather.client import OpenWeatherApi
from .integrations.registry import Integrations
from .integrations.spotify.client import SpotifyApi


def get_config() -> Config:
	# load_config() is itself cached, so this is just a Depends()-friendly alias.
	return load_config()


# Redis connection (rate limiter's hot path — counters and the live blacklist cache).
# redis.asyncio.Redis connects lazily on first command and doesn't need a running
# event loop to construct, so a plain lru_cache singleton is enough.
@lru_cache
def get_redis() -> Redis:
	return Redis.from_url(load_config().redis_url, decode_responses=True)


# The Integrations container (shared aiohttp session + all API clients) is
# created in main.py's lifespan and stashed on app.state; these dependencies
# just read it back per request.
def get_integrations(request: Request) -> Integrations:
	return request.app.state.integrations


def get_spotify_api(request: Request) -> SpotifyApi:
	return get_integrations(request).spotify


def get_hardcover_api(request: Request) -> HardcoverApi:
	return get_integrations(request).hardcover


def get_openweather_api(request: Request) -> OpenWeatherApi:
	return get_integrations(request).openweather


ConfigDep = Annotated[Config, Depends(get_config)]
SpotifyDep = Annotated[SpotifyApi, Depends(get_spotify_api)]
HardcoverDep = Annotated[HardcoverApi, Depends(get_hardcover_api)]
OpenWeatherDep = Annotated[OpenWeatherApi, Depends(get_openweather_api)]
