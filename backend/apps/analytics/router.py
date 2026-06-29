from fastapi import APIRouter, Depends
from .service import AnalyticsService
from .schemas import (
    OverviewResponse,
    TicketAnalyticsResponse,
    CustomerAnalyticsResponse,
    AgentAnalyticsResponse,
    KnowledgeAnalyticsResponse
)
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException

router = APIRouter(prefix="/api/admin/analytics", tags=["analytics"])

def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()

@router.get("/overview", response_model=SuccessResponse[OverviewResponse])
async def get_overview(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        result = service.get_overview()
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/tickets", response_model=SuccessResponse[TicketAnalyticsResponse])
async def get_ticket_analytics(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        result = service.get_ticket_analytics()
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/customers", response_model=SuccessResponse[CustomerAnalyticsResponse])
async def get_customer_analytics(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        result = service.get_customer_analytics()
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/agents", response_model=SuccessResponse[AgentAnalyticsResponse])
async def get_agent_analytics(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        result = service.get_agent_analytics()
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/knowledge", response_model=SuccessResponse[KnowledgeAnalyticsResponse])
async def get_knowledge_analytics(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        result = service.get_knowledge_analytics()
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)
