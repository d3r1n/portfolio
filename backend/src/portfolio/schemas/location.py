from pydantic import BaseModel

from ..integrations.openweather.schemas import CurrentWeather


class CurrentLocationRead(BaseModel):
	location_name: str
	latitude: float
	longitude: float


class CurrentLocationWeather(CurrentLocationRead):
	weather: CurrentWeather | None = None
