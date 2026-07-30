from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ..database import DatabaseDep
from ..schemas.projects import FeaturedProject
from ..security import rate_limit, require_viewer

router = APIRouter(prefix="/projects", tags=["Projects"], dependencies=[Depends(require_viewer), Depends(rate_limit())])


@router.get("/featured", response_model=list[FeaturedProject])
async def featured_projects(
	db: DatabaseDep,
	limit: Annotated[int, Query(ge=1, le=10)] = 2,
) -> list[FeaturedProject]:
	projects = await db.projects.list(limit=limit)

	return [FeaturedProject.model_validate(project, from_attributes=True) for project in projects]
