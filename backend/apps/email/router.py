from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from .service import EmailAdminService
from .schemas import (
    EmailListResponse,
    EmailDetailResponse,
    EmailResponse,
    EmailStatus,
    ReplyRequest,
    ReplyResponse
)
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException
from core.admin_auth import require_admin_auth

router = APIRouter(
    prefix="/api/admin/email",
    tags=["email"],
    dependencies=[Depends(require_admin_auth)]
)

def get_email_service() -> EmailAdminService:
    return EmailAdminService()

@router.get("", response_model=SuccessResponse[EmailListResponse])
async def list_emails(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    status: Optional[EmailStatus] = None,
    search: Optional[str] = None,
    service: EmailAdminService = Depends(get_email_service)
):
    try:
        result = service.list_emails(
            status=status.value if status else None,
            search=search,
            page=page,
            limit=limit
        )
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/search", response_model=SuccessResponse[List[EmailResponse]])
async def search_emails(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=50),
    service: EmailAdminService = Depends(get_email_service)
):
    try:
        results = service.search_emails(query=q, limit=limit)
        return success(data=results)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/{email_id}", response_model=SuccessResponse[EmailDetailResponse])
async def get_email(
    email_id: int,
    service: EmailAdminService = Depends(get_email_service)
):
    try:
        result = service.get_email_detail(email_id)
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.post("/reply", response_model=SuccessResponse[ReplyResponse])
async def send_reply(
    request: ReplyRequest,
    service: EmailAdminService = Depends(get_email_service)
):
    try:
        result = service.send_reply(
            to=request.to,
            subject=request.subject,
            body=request.body
        )
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)

@router.post("/{email_id}/retry", response_model=SuccessResponse[ReplyResponse])
async def retry_email(
    email_id: int,
    service: EmailAdminService = Depends(get_email_service)
):
    try:
        result = service.retry_email(email_id)
        return success(data=result)
    except SupportFlowException as e:
        raise to_http_exception(e)
