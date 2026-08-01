from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from ..database import DatabaseDep
from ..schemas.admin import StatusMessage
from ..schemas.blog import BlogPostDetail, BlogPostListResponse, BlogPostSummary
from ..security import rate_limit, require_viewer

router = APIRouter(prefix="/blog", tags=["Blog"], dependencies=[Depends(require_viewer), Depends(rate_limit())])

not_found_response = {404: {"model": StatusMessage, "description": "Resource not found"}}


@router.get("", response_model=BlogPostListResponse)
async def list_blog_posts(
	db: DatabaseDep,
	limit: Annotated[int, Query(ge=1, le=50)] = 20,
	offset: Annotated[int, Query(ge=0)] = 0,
) -> BlogPostListResponse:
	"""List published posts, newest first."""
	posts = await db.blog_posts.list_published(limit=limit, offset=offset)
	total = await db.blog_posts.count(status="published")

	return BlogPostListResponse(
		items=[BlogPostSummary.model_validate(post, from_attributes=True) for post in posts],
		total=total,
		limit=limit,
		offset=offset,
	)


@router.get("/{slug}", response_model=BlogPostDetail, responses={**not_found_response})
async def get_blog_post(slug: str, db: DatabaseDep) -> BlogPostDetail | JSONResponse:
	"""Get a single post by slug. Drafts are never public; archived posts stay reachable by direct link."""
	post = await db.blog_posts.get_by_slug(slug)

	if post is None or post.status == "draft":
		return JSONResponse(
			status_code=status.HTTP_404_NOT_FOUND,
			content={"status": "error", "message": "Post not found."},
		)

	return BlogPostDetail.model_validate(post, from_attributes=True)
