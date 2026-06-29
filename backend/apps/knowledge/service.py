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

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

class KnowledgeService:

    def __init__(self):
        self.repository = KnowledgeRepository()
        self._vectorstore = None

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain_chroma import Chroma

            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            self._vectorstore = Chroma(
                persist_directory=CHROMA_DB_PATH,
                embedding_function=embeddings
            )
        return self._vectorstore

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

        # Get chunks from ChromaDB
        chunks = self._get_chunks_for_document(document_id)

        response = DocumentDetailResponse(
            id=doc_data['id'],
            title=doc_data['title'],
            type=DocumentType(doc_data['type']),
            status=DocumentStatus(doc_data['status']),
            chunks=doc_data['chunks'],
            retrieval_count=doc_data['retrieval_count'],
            last_updated=doc_data['last_updated'],
            size=self._format_size(doc_data.get('size_bytes', 0)),
            file_path=doc_data.get('file_path'),
            chunk_list=chunks
        )

        return response

    def get_document_chunks(self, document_id: str) -> List[ChunkResponse]:
        self.repository.get_document(document_id)
        return self._get_chunks_for_document(document_id)

    def search_knowledge(self, query: str, k: int = 5) -> SearchResultResponse:
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)

        results = [
            SearchHitResponse(
                chunk_content=doc.page_content,
                similarity_score=round(1 - score, 4),  # Convert distance to similarity
                source_document=doc.metadata.get('source', 'Unknown')
            )
            for doc, score in docs_with_scores
        ]

        return SearchResultResponse(query=query, results=results)

    def upload_document(self, title: str, content: str, doc_type: str) -> UploadResponse:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document

        doc_id = str(uuid.uuid4())

        # Chunk the content
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        documents = [Document(page_content=content, metadata={"source": title, "doc_id": doc_id})]
        chunks = splitter.split_documents(documents)

        # Add to vectorstore
        try:
            self.vectorstore.add_documents(chunks)

            # Save metadata to DB
            self.repository.create_document({
                'id': doc_id,
                'title': title,
                'type': doc_type,
                'status': 'indexed',
                'chunks': len(chunks),
                'retrieval_count': 0,
                'last_updated': datetime.now().isoformat(),
                'size_bytes': len(content.encode('utf-8')),
                'chroma_collection': 'default'
            })

            logger.info(f"Uploaded document '{title}' with {len(chunks)} chunks")

            return UploadResponse(
                id=doc_id,
                title=title,
                chunks_created=len(chunks),
                status=DocumentStatus.INDEXED
            )

        except Exception as e:
            logger.error(f"Failed to upload document: {e}")

            self.repository.create_document({
                'id': doc_id,
                'title': title,
                'type': doc_type,
                'status': 'failed',
                'chunks': 0,
                'retrieval_count': 0,
                'last_updated': datetime.now().isoformat(),
                'size_bytes': len(content.encode('utf-8')),
            })

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
        try:
            collection = self.vectorstore._collection
            results = collection.get(where={"doc_id": document_id})

            if not results or not results.get('documents'):
                return []

            chunks = [
                ChunkResponse(
                    id=results['ids'][i],
                    content=results['documents'][i],
                    order=i,
                    retrieval_count=0
                )
                for i in range(len(results['documents']))
            ]
            return chunks

        except Exception:
            return []

    def _to_response(self, data: dict) -> DocumentResponse:
        return DocumentResponse(
            id=data['id'],
            title=data['title'],
            type=DocumentType(data['type']),
            status=DocumentStatus(data['status']),
            chunks=data['chunks'],
            retrieval_count=data['retrieval_count'],
            last_updated=data['last_updated'],
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
