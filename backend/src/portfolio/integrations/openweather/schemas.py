from pydantic import BaseModel


class CurrentWeather(BaseModel):
	"""Current conditions at a single coordinate, per OpenWeatherMap's `/weather` endpoint."""

	temperature: float
	feels_like: float
	condition: str
	description: str
	icon: str
	humidity: int
	wind_speed: float
	location_name: str
