from typing import Annotated

from aiohttp import ClientSession
from loguru import logger
from pydantic import ConfigDict, Field, ValidationError, validate_call

from ...core.config import Config
from .schemas import CurrentWeather

_STATUS_OK = 200


class WeatherError(Exception):
	"""Errors related to the OpenWeatherMap API."""

	def __init__(self, *args) -> None:
		super().__init__(*args)


class OpenWeatherApi:
	"""A client for interacting with the OpenWeatherMap "Current Weather Data" API.

	Given a coordinate, fetches the current weather conditions there. Authentication
	is handled via an API key provided in the configuration.
	"""

	BASE_URL: str = "https://api.openweathermap.org/"
	CURRENT_WEATHER_ENDPOINT: str = "data/4.0/onecall/current"
	GEOCODING_ENDPOINT: str = "geo/1.0/direct"

	def __init__(self, config: Config) -> None:
		self._API_KEY: str = config.openweathermap.api_key

	async def get_coordinates_from_location_name(
		self, session: ClientSession, location_name: str
	) -> tuple[float, float] | None:
		"""Fetch the coordinates (latitude, longitude) for a given location name.

		Args:
			session (ClientSession): aiohttp client session for making requests
			location_name (str): The name of the location to look up

		Returns:
			tuple[float, float] | None: A tuple containing (latitude, longitude)

		Raises:
			WeatherError: if the OpenWeatherMap API returns anything except `200 (OK)`
		"""
		if not self._API_KEY:
			logger.warning("OpenWeatherMap API key is not configured. Skipping request.")
			return None

		params = {
			"q": location_name,
			"limit": 1,  # Only need the first result
			"appid": self._API_KEY,
		}

		response = await session.get(f"{self.BASE_URL}{self.GEOCODING_ENDPOINT}", params=params)

		if response.status != _STATUS_OK:
			raise WeatherError({"status_code": response.status, "message": await response.text()})

		data = await response.json()

		if not data:
			logger.warning(f"No coordinates found for location name: {location_name}")
			return None

		latitude = data[0]["lat"]
		longitude = data[0]["lon"]

		return latitude, longitude

	@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
	async def get_current_weather(
		self,
		session: ClientSession,
		*,  # pydantic keyword only
		latitude: Annotated[float, Field(ge=-90, le=90)],
		longitude: Annotated[float, Field(ge=-180, le=180)],
	) -> CurrentWeather | None:
		"""Fetch the current weather conditions for a coordinate.

		Args:
			session (ClientSession): aiohttp client session for making requests
			latitude (float): -90 <= latitude <= 90
			longitude (float): -180 <= longitude <= 180

		Returns:
			CurrentWeather | None: the current conditions, or None if no API key is configured.

		Raises:
			WeatherError: if the OpenWeatherMap API returns anything except `200 (OK)`
		"""
		if not self._API_KEY:
			logger.warning("OpenWeatherMap API key is not configured. Skipping request.")
			return None

		params = {
			"lat": latitude,
			"lon": longitude,
			"appid": self._API_KEY,
			"units": "metric",  # Celsius, meters/sec wind speed
		}

		response = await session.get(self.BASE_URL, params=params)

		if response.status != _STATUS_OK:
			raise WeatherError({"status_code": response.status, "message": await response.text()})

		json_data = await response.json()
		logger.debug(f"OpenWeatherMap API response data: {json_data}")

		try:
			weather = json_data["weather"][0]
			main = json_data["main"]
			wind = json_data.get("wind", {})

			return CurrentWeather(
				temperature=main["temp"],
				feels_like=main["feels_like"],
				condition=weather["main"],
				description=weather["description"],
				icon=weather["icon"],
				humidity=main["humidity"],
				wind_speed=wind.get("speed", 0.0),
				location_name=json_data.get("name") or "Unknown",
			)
		except (KeyError, IndexError, ValidationError) as exc:
			logger.error(f"Failed parsing OpenWeatherMap response. Error: {exc}")
			raise WeatherError(
				{"status_code": _STATUS_OK, "message": f"OpenWeatherMap response validation failed: {exc}"}
			) from exc
