import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from ..core.text import estimate_reading_minutes, slugify
from ..database import DatabaseDep
from ..database.dto import BlogPostData, ProjectData
from ..deps import OpenWeatherDep
from ..integrations.openweather.client import WeatherError
from ..schemas.admin import (
	BlogPostCreate,
	BlogPostListResponse,
	BlogPostRead,
	BlogPostStatusUpdate,
	BlogPostUpdate,
	ProjectCreate,
	ProjectRead,
	ProjectUpdate,
	StatusMessage,
)
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


async def _unique_slug(db: DatabaseDep, title: str) -> str:
	"""Slugify `title`, disambiguating with a numeric suffix on collision."""
	base = slugify(title)
	slug = base
	suffix = 2
	while await db.blog_posts.slug_exists(slug):
		slug = f"{base}-{suffix}"
		suffix += 1
	return slug


@router.get("/blog", response_model=BlogPostListResponse)
async def list_blog_posts(
	db: DatabaseDep,
	post_status: Annotated[str | None, Query(alias="status")] = None,
	limit: Annotated[int, Query(ge=1, le=100)] = 20,
	offset: Annotated[int, Query(ge=0)] = 0,
) -> BlogPostListResponse:
	"""List all posts regardless of status, newest first."""
	posts = await db.blog_posts.list(status=post_status, limit=limit, offset=offset)
	total = await db.blog_posts.count(status=post_status)

	return BlogPostListResponse(
		items=[BlogPostRead.model_validate(post, from_attributes=True) for post in posts],
		total=total,
		limit=limit,
		offset=offset,
	)


@router.get("/blog/{post_id}", response_model=BlogPostRead, responses={**not_found_response})
async def get_blog_post(post_id: uuid.UUID, db: DatabaseDep) -> BlogPostRead | JSONResponse:
	"""Get a single post by id."""
	post = await db.blog_posts.get(post_id)

	if post is None:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Post not found."},
		)

	return BlogPostRead.model_validate(post, from_attributes=True)


@router.post("/blog", response_model=BlogPostRead, status_code=status.HTTP_201_CREATED)
async def create_blog_post(payload: BlogPostCreate, db: DatabaseDep) -> BlogPostRead:
	"""Create a new post. Always starts in "draft" status — publish separately."""
	slug = await _unique_slug(db, payload.title)
	reading_time_minutes = estimate_reading_minutes(payload.content)

	post = await db.blog_posts.create(
		BlogPostData(**payload.model_dump(mode="json")),
		slug=slug,
		reading_time_minutes=reading_time_minutes,
	)

	return BlogPostRead.model_validate(post, from_attributes=True)


@router.patch("/blog/{post_id}", response_model=BlogPostRead, responses={**not_found_response})
async def update_blog_post(
	post_id: uuid.UUID, payload: BlogPostUpdate, db: DatabaseDep
) -> BlogPostRead | JSONResponse:
	"""Update an existing post's content. Only the fields present in the request body are changed."""
	changes = payload.model_dump(mode="json", exclude_unset=True)
	if "content" in changes:
		changes["reading_time_minutes"] = estimate_reading_minutes(changes["content"])

	post = await db.blog_posts.update(post_id, changes)

	if post is None:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Post not found."},
		)

	return BlogPostRead.model_validate(post, from_attributes=True)


@router.patch("/blog/{post_id}/status", response_model=BlogPostRead, responses={**not_found_response})
async def set_blog_post_status(
	post_id: uuid.UUID, payload: BlogPostStatusUpdate, db: DatabaseDep
) -> BlogPostRead | JSONResponse:
	"""Transition a post between draft, published, and archived."""
	post = await db.blog_posts.set_status(post_id, payload.status)

	if post is None:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Post not found."},
		)

	return BlogPostRead.model_validate(post, from_attributes=True)


@router.delete("/blog/{post_id}", response_model=StatusMessage, responses={**not_found_response})
async def delete_blog_post(post_id: uuid.UUID, db: DatabaseDep) -> StatusMessage | JSONResponse:
	"""Delete a post."""
	deleted = await db.blog_posts.delete(post_id)

	if not deleted:
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Post not found."},
		)

	return StatusMessage(status="success", message="Post deleted successfully.")
