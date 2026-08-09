import os
import uuid
from typing import Optional, List
from datetime import datetime
from .repository import KnowledgeRepository
from .schemas import (
    DocumentResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    ChunkResponse,
    SearchResultResponse,
    SearchHitResponse,
    StatisticsResponse,
    UploadResponse,
    DocumentStatus,
    DocumentType
)
from core.logging_config import get_logger

logger = get_logger(__name__)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class KnowledgeService:

    def __init__(self):
        self.repository = KnowledgeRepository()
        self._embeddings = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            from langchain_huggingface import HuggingFaceEmbeddings
            self._embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        return self._embeddings

    def list_documents(
        self,
        doc_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> DocumentListResponse:

        offset = (page - 1) * limit

        documents_data, total = self.repository.list_documents(
            doc_type=doc_type,
            status=status,
            search=search,
            limit=limit,
            offset=offset
        )

        documents = [self._to_response(d) for d in documents_data]

        return DocumentListResponse(
            documents=documents,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0
        )

    def get_document_detail(self, document_id: str) -> DocumentDetailResponse:
        doc_data = self.repository.get_document(document_id)
        chunks = self._get_chunks_for_document(document_id)

        response = DocumentDetailResponse(
            id=doc_data['id'],
            title=doc_data['title'],
            type=DocumentType(doc_data['type']),
            status=DocumentStatus(doc_data['status']),
            chunks=doc_data['chunks'],
            retrieval_count=doc_data['retrieval_count'],
            last_updated=str(doc_data['last_updated']),
            size=self._format_size(doc_data.get('size_bytes', 0)),
            file_path=doc_data.get('file_path'),
            chunk_list=chunks
        )

        return response

    def get_document_chunks(self, document_id: str) -> List[ChunkResponse]:
        self.repository.get_document(document_id)
        return self._get_chunks_for_document(document_id)

    def search_knowledge(self, query: str, k: int = 5) -> SearchResultResponse:
        query_vec = self.embeddings.embed_query(query)
        hits = self.repository.vector_similarity_search(query_vec, top_k=k)

        results = [
            SearchHitResponse(
                chunk_content=h['content'],
                similarity_score=round(float(h['similarity_score']), 4),
                source_document=h['document_title']
            )
            for h in hits
        ]

        return SearchResultResponse(query=query, results=results)

    def upload_document(self, title: str, content: str, doc_type: str) -> UploadResponse:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_core.documents import Document

        doc_id = str(uuid.uuid4())

        self.repository.create_document({
            'id': doc_id,
            'title': title,
            'type': doc_type,
            'status': 'pending',
            'chunks': 0,
            'retrieval_count': 0,
            'last_updated': datetime.utcnow().isoformat(),
            'size_bytes': len(content.encode('utf-8')),
            'metadata': {'source': title, 'doc_id': doc_id}
        })

        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            docs = [Document(page_content=content, metadata={"source": title, "doc_id": doc_id})]
            split_chunks = splitter.split_documents(docs)

            chunks_data = []
            for idx, ch in enumerate(split_chunks):
                emb = self.embeddings.embed_query(ch.page_content)
                chunks_data.append({
                    'id': f"{doc_id}#chunk_{idx}",
                    'content': ch.page_content,
                    'embedding': emb,
                    'metadata': {"source": title, "doc_id": doc_id, "chunk_index": idx}
                })

            self.repository.replace_document_chunks(doc_id, chunks_data)

            logger.info(f"Uploaded document '{title}' with {len(chunks_data)} chunks to PostgreSQL pgvector")

            return UploadResponse(
                id=doc_id,
                title=title,
                chunks_created=len(chunks_data),
                status=DocumentStatus.INDEXED
            )

        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            self.repository.update_document_status(doc_id, 'failed', 0)

            return UploadResponse(
                id=doc_id,
                title=title,
                chunks_created=0,
                status=DocumentStatus.FAILED
            )

    def delete_document(self, document_id: str) -> None:
        self.repository.delete_document(document_id)
        logger.info(f"Document {document_id} deleted")

    def get_statistics(self) -> StatisticsResponse:
        stats = self.repository.get_statistics()
        return StatisticsResponse(**stats)

    def _get_chunks_for_document(self, document_id: str) -> List[ChunkResponse]:
        chunks_raw = self.repository.retrieve_document_chunks(document_id)
        return [
            ChunkResponse(
                id=c['id'],
                content=c['content'],
                order=c['chunk_index'],
                retrieval_count=0
            )
            for c in chunks_raw
        ]

    def _to_response(self, data: dict) -> DocumentResponse:
        try:
            doc_type = DocumentType(data['type'])
        except ValueError:
            doc_type = DocumentType.TXT

        try:
            doc_status = DocumentStatus(data['status'])
        except ValueError:
            doc_status = DocumentStatus.PENDING

        return DocumentResponse(
            id=data['id'],
            title=data['title'],
            type=doc_type,
            status=doc_status,
            chunks=data['chunks'],
            retrieval_count=data['retrieval_count'],
            last_updated=str(data['last_updated']),
            size=self._format_size(data.get('size_bytes', 0)),
            file_path=data.get('file_path')
        )

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "Unknown"
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"
