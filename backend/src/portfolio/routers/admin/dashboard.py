from fastapi import APIRouter, Depends

from ...lib.security import rate_limit, require_admin

router = APIRouter(
	prefix="/admin/dashboard", tags=["Admin Dashboard"], dependencies=[Depends(require_admin), Depends(rate_limit())]
)


@router.post("/set-current-location")
async def set_current_location():
	pass
