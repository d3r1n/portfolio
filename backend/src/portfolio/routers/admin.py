import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from ..database import DatabaseDep
from ..database.dto import ProjectData
from ..deps import OpenWeatherDep
from ..integrations.openweather.client import WeatherError
from ..schemas.admin import ProjectCreate, ProjectRead, ProjectUpdate, StatusMessage
from ..schemas.location import CurrentLocationRead
from ..security import rate_limit, require_admin

router = APIRouter(
	prefix="/admin/dashboard", tags=["Admin Dashboard"], dependencies=[Depends(require_admin), Depends(rate_limit())]
)

not_found_response = {404: {"model": StatusMessage, "description": "Resource not found"}}


@router.post(
	"/set-current-location",
	response_model=CurrentLocationRead,
	responses={
		400: {"model": StatusMessage, "description": "The geocoding lookup failed"},
		404: {"model": StatusMessage, "description": "Location name did not resolve to a place"},
	},
)
async def set_current_location(
	db: DatabaseDep,
	api: OpenWeatherDep,
	location_name: str = Query(min_length=2, max_length=128, pattern=r"^[a-zA-z\s]+,[\s]*[a-zA-z]+$"),
) -> CurrentLocationRead | JSONResponse:
	"""Resolve `location_name` via OpenWeatherMap's geocoding API and store it as the current location."""
	# A failed lookup here is the admin's bad input, not an upstream outage,
	# so it maps to 400 instead of the app-wide 502 handler.
	try:
		geocoding = await api.get_coordinates_from_location_name(location_name)
	except WeatherError as error:
		return JSONResponse(
			status_code=status.HTTP_400_BAD_REQUEST,
			content={"status": "error", "message": f"Failed to set current location: {error.message}"},
		)

	if geocoding is None:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Location not found."},
		)

	current_location = await db.locations.set_current(
		location_name=location_name,
		latitude=geocoding.lat,
		longitude=geocoding.lon,
	)

	return CurrentLocationRead.model_validate(current_location, from_attributes=True)


@router.get("/get-current-location", response_model=CurrentLocationRead, responses={**not_found_response})
async def get_current_location(db: DatabaseDep) -> CurrentLocationRead | JSONResponse:
	"""Get the current location for the portfolio."""
	current_location = await db.locations.get_current()

	if current_location is None:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Current location not set."},
		)

	return CurrentLocationRead.model_validate(current_location, from_attributes=True)


@router.get("/projects", response_model=list[ProjectRead])
async def list_projects(db: DatabaseDep) -> list[ProjectRead]:
	"""List all projects."""
	projects = await db.projects.list()

	return [ProjectRead.model_validate(project, from_attributes=True) for project in projects]


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: DatabaseDep) -> ProjectRead:
	"""Add a new project."""
	project = await db.projects.create(ProjectData(**payload.model_dump(mode="json")))

	return ProjectRead.model_validate(project, from_attributes=True)


@router.patch("/projects/{project_id}", response_model=ProjectRead, responses={**not_found_response})
async def update_project(project_id: uuid.UUID, payload: ProjectUpdate, db: DatabaseDep) -> ProjectRead | JSONResponse:
	"""Update an existing project. Only the fields present in the request body are changed."""
	project = await db.projects.update(project_id, payload.model_dump(mode="json", exclude_unset=True))

	if project is None:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Project not found."},
		)

	return ProjectRead.model_validate(project, from_attributes=True)


@router.delete("/projects/{project_id}", response_model=StatusMessage, responses={**not_found_response})
async def delete_project(project_id: uuid.UUID, db: DatabaseDep) -> StatusMessage | JSONResponse:
	"""Delete a project."""
	deleted = await db.projects.delete(project_id)

	if not deleted:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Project not found."},
		)

	return StatusMessage(status="success", message="Project deleted successfully.")
