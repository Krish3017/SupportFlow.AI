from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from .service import ConversationService
from .schemas import (
    ConversationListResponse,
    ConversationDetailResponse,
    MessageResponse,
    ConversationResponse,
    Channel,
    ConversationStatus
)
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/admin/conversations", tags=["conversations"])

def get_conversation_service() -> ConversationService:
    return ConversationService()

@router.get("", response_model=SuccessResponse[ConversationListResponse])
async def list_conversations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    customer_id: Optional[str] = None,
    channel: Optional[Channel] = None,
    status: Optional[ConversationStatus] = None,
    ticket_id: Optional[str] = None,
    search: Optional[str] = None,
    service: ConversationService = Depends(get_conversation_service)
):
    try:
        result = service.list_conversations(
            customer_id=customer_id,
            channel=channel.value if channel else None,
            status=status.value if status else None,
            ticket_id=ticket_id,
            search=search,
            page=page,
            limit=limit
        )
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/search", response_model=SuccessResponse[List[ConversationResponse]])
async def search_conversations(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=50),
    service: ConversationService = Depends(get_conversation_service)
):
    try:
        results = service.search_conversations(query=q, limit=limit)
        return success(data=results)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/{conversation_id}", response_model=SuccessResponse[ConversationDetailResponse])
async def get_conversation(
    conversation_id: str,
    service: ConversationService = Depends(get_conversation_service)
):
    try:
        conversation = service.get_conversation_detail(conversation_id)
        return success(data=conversation)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/{conversation_id}/messages", response_model=SuccessResponse[List[MessageResponse]])
async def get_messages(
    conversation_id: str,
    service: ConversationService = Depends(get_conversation_service)
):
    try:
        messages = service.get_messages(conversation_id)
        return success(data=messages)

    except SupportFlowException as e:
        raise to_http_exception(e)
