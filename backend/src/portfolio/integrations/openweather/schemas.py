from pydantic import BaseModel


class CurrentWeather(BaseModel):
	"""Current conditions at a single coordinate, per OpenWeatherMap's `/onecall` endpoint."""

	temperature: float
	feels_like: float
	condition: str
	description: str
	weather_id: int
	humidity: int
	wind_speed: float
	dt: int
	timezone: int


class Geocoding(BaseModel):
	"""Geocoding information for a single coordinate, per OpenWeatherMap's `/geo/1.0/direct` endpoint."""

	# ignoring local names, not relevant for my use

	name: str
	lat: float
	lon: float
	country: str
	state: str | None = None
