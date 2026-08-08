from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from .service import CustomerService
from .schemas import (
    CustomerListResponse,
    CustomerDetailResponse,
    CustomerResponse,
    TicketSummary,
    ConversationSummary,
    CustomerTier,
    Sentiment
)
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException
from core.logging_config import get_logger

from core.admin_auth import require_admin_auth

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/admin/customers",
    tags=["customers"],
    dependencies=[Depends(require_admin_auth)]
)

def get_customer_service() -> CustomerService:
    return CustomerService()

@router.get("", response_model=SuccessResponse[CustomerListResponse])
async def list_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    tier: Optional[CustomerTier] = None,
    sentiment: Optional[Sentiment] = None,
    min_risk_score: Optional[int] = Query(default=None, ge=0, le=100),
    max_risk_score: Optional[int] = Query(default=None, ge=0, le=100),
    search: Optional[str] = None,
    service: CustomerService = Depends(get_customer_service)
):
    try:
        result = service.list_customers(
            tier=tier.value if tier else None,
            sentiment=sentiment.value if sentiment else None,
            min_risk_score=min_risk_score,
            max_risk_score=max_risk_score,
            search=search,
            page=page,
            limit=limit
        )
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/search", response_model=SuccessResponse[List[CustomerResponse]])
async def search_customers(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=50),
    service: CustomerService = Depends(get_customer_service)
):
    try:
        results = service.search_customers(query=q, limit=limit)
        return success(data=results)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/{customer_id}", response_model=SuccessResponse[CustomerDetailResponse])
async def get_customer(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    try:
        customer = service.get_customer_detail(customer_id)
        return success(data=customer)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/{customer_id}/tickets", response_model=SuccessResponse[List[TicketSummary]])
async def get_customer_tickets(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    try:
        tickets = service.get_customer_tickets(customer_id)
        return success(data=tickets)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/{customer_id}/conversations", response_model=SuccessResponse[List[ConversationSummary]])
async def get_customer_conversations(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    try:
        conversations = service.get_customer_conversations(customer_id)
        return success(data=conversations)

    except SupportFlowException as e:
        raise to_http_exception(e)
