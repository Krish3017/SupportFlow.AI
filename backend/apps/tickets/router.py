"""
Ticket Module Router
Admin API endpoints for ticket management
"""
from fastapi import APIRouter, Query, Depends
from typing import Optional
from .service import TicketService
from .schemas import (
    TicketListQuery,
    TicketListResponse,
    TicketDetailResponse,
    UpdateTicketStatusRequest,
    Priority,
    Status,
    Channel
)
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException
from core.logging_config import get_logger

from core.admin_auth import require_admin_auth

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/admin/tickets",
    tags=["tickets"],
    dependencies=[Depends(require_admin_auth)]
)

# Dependency
def get_ticket_service() -> TicketService:
    return TicketService()

@router.get("", response_model=SuccessResponse[TicketListResponse])
async def list_tickets(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    status: Optional[Status] = None,
    priority: Optional[Priority] = None,
    channel: Optional[Channel] = None,
    search: Optional[str] = None,
    service: TicketService = Depends(get_ticket_service)
):
    """
    List tickets with filters and pagination

    - **page**: Page number (1-indexed)
    - **limit**: Items per page (max 100)
    - **status**: Filter by status (new, in_progress, resolved, escalated)
    - **priority**: Filter by priority (critical, high, medium, low)
    - **channel**: Filter by channel (email, chat, telegram)
    - **search**: Search in ticket subject
    """
    try:
        result = service.list_tickets(
            status=status.value if status else None,
            priority=priority.value if priority else None,
            channel=channel.value if channel else None,
            search=search,
            page=page,
            limit=limit
        )
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/{ticket_id}", response_model=SuccessResponse[TicketDetailResponse])
async def get_ticket(
    ticket_id: str,
    service: TicketService = Depends(get_ticket_service)
):
    """
    Get detailed ticket information

    Includes:
    - Basic ticket info
    - Full conversation history
    - Agent execution trace
    - Total latency and cost
    """
    try:
        ticket = service.get_ticket_detail(ticket_id)
        return success(data=ticket)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.patch("/{ticket_id}/status", response_model=SuccessResponse[dict])
async def update_ticket_status(
    ticket_id: str,
    request: UpdateTicketStatusRequest,
    service: TicketService = Depends(get_ticket_service)
):
    """
    Update ticket status

    Valid statuses: new, in_progress, resolved, escalated
    """
    try:
        service.update_ticket_status(ticket_id, request.status.value)
        return success(
            data={"ticket_id": ticket_id, "status": request.status.value},
            message="Ticket status updated successfully"
        )

    except SupportFlowException as e:
        raise to_http_exception(e)
