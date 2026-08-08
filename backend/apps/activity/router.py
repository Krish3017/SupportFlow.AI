from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from .service import ActivityService
from .schemas import (
    ActivityListResponse,
    ActivityResponse,
    ActivityType,
    ActivityLevel
)
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException

from core.admin_auth import require_admin_auth

router = APIRouter(
    prefix="/api/admin/activity",
    tags=["activity"],
    dependencies=[Depends(require_admin_auth)]
)

def get_activity_service() -> ActivityService:
    return ActivityService()

@router.get("", response_model=SuccessResponse[ActivityListResponse])
async def list_activities(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    type: Optional[ActivityType] = None,
    level: Optional[ActivityLevel] = None,
    search: Optional[str] = None,
    service: ActivityService = Depends(get_activity_service)
):
    try:
        result = service.list_activities(
            activity_type=type.value if type else None,
            level=level.value if level else None,
            search=search,
            page=page,
            limit=limit
        )
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/search", response_model=SuccessResponse[List[ActivityResponse]])
async def search_activities(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=50),
    service: ActivityService = Depends(get_activity_service)
):
    try:
        results = service.search_activities(query=q, limit=limit)
        return success(data=results)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/{activity_id}", response_model=SuccessResponse[ActivityResponse])
async def get_activity(
    activity_id: int,
    service: ActivityService = Depends(get_activity_service)
):
    try:
        result = service.get_activity(activity_id)
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)
