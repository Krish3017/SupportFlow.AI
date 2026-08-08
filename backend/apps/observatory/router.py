from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from .service import ObservatoryService
from .schemas import (
    AgentListResponse,
    AgentDetailResponse,
    ExecutionListResponse,
    ExecutionDetailResponse,
    ExecutionStepResponse,
    ExecutionStatusEnum
)
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException
from core.logging_config import get_logger

from core.admin_auth import require_admin_auth

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/admin/observatory",
    tags=["observatory"],
    dependencies=[Depends(require_admin_auth)]
)

def get_observatory_service() -> ObservatoryService:
    return ObservatoryService()

@router.get("/agents", response_model=SuccessResponse[AgentListResponse])
async def list_agents(
    service: ObservatoryService = Depends(get_observatory_service)
):
    try:
        result = service.get_all_agents()
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/agents/{agent_name}", response_model=SuccessResponse[AgentDetailResponse])
async def get_agent(
    agent_name: str,
    service: ObservatoryService = Depends(get_observatory_service)
):
    try:
        result = service.get_agent_detail(agent_name)
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/executions", response_model=SuccessResponse[ExecutionListResponse])
async def list_executions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    agent_id: Optional[str] = None,
    status: Optional[ExecutionStatusEnum] = None,
    ticket_id: Optional[str] = None,
    search: Optional[str] = None,
    service: ObservatoryService = Depends(get_observatory_service)
):
    try:
        result = service.list_executions(
            agent_id=agent_id,
            status=status.value if status else None,
            ticket_id=ticket_id,
            search=search,
            page=page,
            limit=limit
        )
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/executions/{execution_id}", response_model=SuccessResponse[ExecutionDetailResponse])
async def get_execution(
    execution_id: str,
    service: ObservatoryService = Depends(get_observatory_service)
):
    try:
        result = service.get_execution_detail(execution_id)
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/executions/{execution_id}/timeline", response_model=SuccessResponse[List[ExecutionStepResponse]])
async def get_execution_timeline(
    execution_id: str,
    service: ObservatoryService = Depends(get_observatory_service)
):
    try:
        result = service.get_execution_timeline(execution_id)
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)
