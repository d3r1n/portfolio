from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from ..database import DatabaseDep
from ..deps import OpenWeatherDep
from ..schemas.errors import upstream_error_response
from ..schemas.location import CurrentLocationWeather
from ..security import rate_limit, require_viewer

router = APIRouter(prefix="/location", tags=["Location"], dependencies=[Depends(require_viewer), Depends(rate_limit())])

weather_error_response = upstream_error_response(
	"The OpenWeatherMap API returned an error", "OpenWeatherMap response validation failed"
)


@router.get(
	"/current",
	response_model=CurrentLocationWeather,
	responses={404: {"description": "Current location not set"}, **weather_error_response},
)
async def current_location_and_weather(db: DatabaseDep, api: OpenWeatherDep) -> CurrentLocationWeather | Response:
	"""Get the site owner's current location and the weather conditions there."""
	current_location = await db.locations.get_current()

	if current_location is None:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Current location not set."},
		)

	weather = await api.get_current_weather(latitude=current_location.latitude, longitude=current_location.longitude)

	return CurrentLocationWeather(
		location_name=current_location.location_name,
		latitude=current_location.latitude,
		longitude=current_location.longitude,
		weather=weather,
	)
