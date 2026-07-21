from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ..schemas.projects import FeaturedProject, ProjectLink
from ..security import rate_limit, require_viewer

router = APIRouter(prefix="/projects", tags=["Projects"], dependencies=[Depends(require_viewer), Depends(rate_limit())])


_FEATURED_PROJECTS: tuple[FeaturedProject, ...] = (
	FeaturedProject(
		name="Project Atlas",
		description="A restrained portfolio and writing hub focused on content hierarchy and speed.",
		year="2026",
		status="Live",
		tags=["Svelte", "Tailwind", "DaisyUI"],
		href="https://github.com/d3r1n/portfolio",
		links=[
			ProjectLink(label="Repository", href="https://github.com/d3r1n/portfolio"),
		],
		accent="01",
	),
	FeaturedProject(
		name="Signal Room",
		description="A compact personal signal dashboard blending books, music, and context widgets.",
		year="2025",
		status="Ongoing",
		tags=["UX", "Data", "Frontend"],
		href="https://github.com/d3r1n",
		links=[
			ProjectLink(label="Profile", href="https://github.com/d3r1n"),
		],
		accent="02",
	),
)


@router.get("/featured", response_model=list[FeaturedProject])
async def featured_projects(
	limit: Annotated[int, Query(ge=1, le=10)] = 2,
) -> list[FeaturedProject]:
	return list(_FEATURED_PROJECTS[:limit])
