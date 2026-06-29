from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    MD = "md"

class DocumentStatus(str, Enum):
    INDEXED = "indexed"
    PENDING = "pending"
    FAILED = "failed"

class DocumentResponse(BaseModel):
    id: str
    title: str
    type: DocumentType
    status: DocumentStatus
    chunks: int
    retrieval_count: int
    last_updated: datetime
    size: str
    file_path: Optional[str] = None

class DocumentDetailResponse(DocumentResponse):
    chunk_list: List['ChunkResponse'] = []

class ChunkResponse(BaseModel):
    id: str
    content: str
    order: int
    retrieval_count: int = 0

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    limit: int
    pages: int

class SearchResultResponse(BaseModel):
    query: str
    results: List['SearchHitResponse']

class SearchHitResponse(BaseModel):
    chunk_content: str
    similarity_score: float
    source_document: Optional[str] = None

class StatisticsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    indexed_documents: int
    failed_documents: int
    pending_documents: int
    total_retrievals: int

class UploadResponse(BaseModel):
    id: str
    title: str
    chunks_created: int
    status: DocumentStatus
