from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from pydantic import BaseModel
from .service import KnowledgeService
from .schemas import (
    DocumentListResponse,
    DocumentDetailResponse,
    ChunkResponse,
    SearchResultResponse,
    StatisticsResponse,
    UploadResponse,
    DocumentType,
    DocumentStatus
)
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException
from core.logging_config import get_logger

from core.admin_auth import require_admin_auth

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/admin/knowledge",
    tags=["knowledge"],
    dependencies=[Depends(require_admin_auth)]
)

def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()

class UploadRequest(BaseModel):
    title: str
    content: str
    type: DocumentType = DocumentType.TXT

class SearchRequest(BaseModel):
    query: str
    k: int = 5

@router.get("/documents", response_model=SuccessResponse[DocumentListResponse])
async def list_documents(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None,
    search: Optional[str] = None,
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        result = service.list_documents(
            doc_type=type.value if type else None,
            status=status.value if status else None,
            search=search,
            page=page,
            limit=limit
        )
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/statistics", response_model=SuccessResponse[StatisticsResponse])
async def get_statistics(
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        result = service.get_statistics()
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/documents/{document_id}", response_model=SuccessResponse[DocumentDetailResponse])
async def get_document(
    document_id: str,
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        result = service.get_document_detail(document_id)
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.get("/documents/{document_id}/chunks", response_model=SuccessResponse[List[ChunkResponse]])
async def get_document_chunks(
    document_id: str,
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        result = service.get_document_chunks(document_id)
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.post("/upload", response_model=SuccessResponse[UploadResponse])
async def upload_document(
    request: UploadRequest,
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        result = service.upload_document(
            title=request.title,
            content=request.content,
            doc_type=request.type.value
        )
        return success(data=result, message="Document uploaded successfully")

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.delete("/documents/{document_id}", response_model=SuccessResponse[dict])
async def delete_document(
    document_id: str,
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        service.delete_document(document_id)
        return success(data={"document_id": document_id}, message="Document deleted")

    except SupportFlowException as e:
        raise to_http_exception(e)

@router.post("/search", response_model=SuccessResponse[SearchResultResponse])
async def search_knowledge(
    request: SearchRequest,
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        result = service.search_knowledge(query=request.query, k=request.k)
        return success(data=result)

    except SupportFlowException as e:
        raise to_http_exception(e)
