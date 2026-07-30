from typing import Any

from aiohttp import ClientSession
from loguru import logger
from pydantic import ValidationError

from ...core.config import Config
from .. import UpstreamError
from .schemas import CurrentWeather, Geocoding


class WeatherError(UpstreamError):
	service = "OpenWeatherMap"


class OpenWeatherApi:
	"""Client for OpenWeatherMap, bound to the app-wide aiohttp session.

	Resolves location names to coordinates and fetches current conditions.
	Authentication is an API key from the configuration.
	"""

	BASE_URL = "https://api.openweathermap.org"

	def __init__(self, config: Config, session: ClientSession) -> None:
		self._session = session
		self._api_key = config.openweathermap.api_key

	async def _get(self, path: str, **params: Any) -> Any:
		"""GET an API path with the key attached. Returns None if no key is configured."""
		if not self._api_key:
			logger.warning("OpenWeatherMap API key is not configured. Skipping request.")
			return None

		response = await self._session.get(f"{self.BASE_URL}{path}", params={**params, "appid": self._api_key})

		if response.status != 200:
			raise WeatherError(await response.text(), status_code=response.status)

		return await response.json()

	async def get_coordinates_from_location_name(self, location_name: str) -> Geocoding | None:
		"""Resolve a location name to coordinates via the geocoding endpoint."""
		data = await self._get("/geo/1.0/direct", q=location_name, limit=1)
		if data is None:
			return None

		try:
			return Geocoding(**data[0])
		except (KeyError, IndexError, ValidationError) as exc:
			logger.error(f"Failed parsing OpenWeatherMap geocoding response: {exc}")
			raise WeatherError(f"OpenWeatherMap geocoding response validation failed: {exc}") from exc

	async def get_current_weather(self, *, latitude: float, longitude: float) -> CurrentWeather | None:
		"""Current conditions at a coordinate (metric units), or None if no API key is configured."""
		data = await self._get("/data/2.5/weather", lat=latitude, lon=longitude, units="metric")
		if data is None:
			return None

		logger.debug(f"OpenWeatherMap API response data: {data}")

		try:
			weather = data["weather"][0]
			main = data["main"]

			return CurrentWeather(
				temperature=main["temp"],
				feels_like=main["feels_like"],
				condition=weather["main"],
				description=weather["description"],
				weather_id=weather["id"],
				humidity=main["humidity"],
				wind_speed=data["wind"]["speed"],
				dt=data["dt"],
				timezone=data["timezone"],
			)
		except (KeyError, IndexError, ValidationError) as exc:
			logger.error(f"Failed parsing OpenWeatherMap response: {exc}")
			raise WeatherError(f"OpenWeatherMap response validation failed: {exc}") from exc
