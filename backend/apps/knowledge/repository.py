import os
from typing import Optional, List, Dict, Tuple
from repositories.base import BaseRepository
from core.errors import NotFoundError
from core.logging_config import get_logger

logger = get_logger(__name__)

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

class KnowledgeRepository(BaseRepository):

    def list_documents(
        self,
        doc_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:

        query = "SELECT * FROM knowledge_documents WHERE 1=1"
        params = []

        if doc_type:
            query += " AND type = ?"
            params.append(doc_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        if search:
            query += " AND title LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY last_updated DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        documents = self._execute_query(query, tuple(params), fetch_all=True)

        count_query = "SELECT COUNT(*) as count FROM knowledge_documents WHERE 1=1"
        count_params = []

        if doc_type:
            count_query += " AND type = ?"
            count_params.append(doc_type)
        if status:
            count_query += " AND status = ?"
            count_params.append(status)
        if search:
            count_query += " AND title LIKE ?"
            count_params.append(f"%{search}%")

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return documents or [], total

    def get_document(self, document_id: str) -> Dict:
        query = "SELECT * FROM knowledge_documents WHERE id = ?"
        doc = self._execute_query(query, (document_id,), fetch_one=True)

        if not doc:
            raise NotFoundError(resource="Document", identifier=document_id)

        return doc

    def create_document(self, doc_data: dict) -> str:
        query = """
            INSERT INTO knowledge_documents
            (id, title, type, status, chunks, retrieval_count, last_updated, size_bytes, file_path, chroma_collection)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self._execute_query(query, (
            doc_data['id'],
            doc_data['title'],
            doc_data['type'],
            doc_data['status'],
            doc_data['chunks'],
            doc_data.get('retrieval_count', 0),
            doc_data['last_updated'],
            doc_data.get('size_bytes', 0),
            doc_data.get('file_path'),
            doc_data.get('chroma_collection', 'default')
        ))
        return doc_data['id']

    def delete_document(self, document_id: str) -> None:
        self.get_document(document_id)  # Verify exists
        query = "DELETE FROM knowledge_documents WHERE id = ?"
        self._execute_query(query, (document_id,))
        logger.info(f"Deleted document {document_id}")

    def increment_retrieval_count(self, document_id: str) -> None:
        query = "UPDATE knowledge_documents SET retrieval_count = retrieval_count + 1 WHERE id = ?"
        self._execute_query(query, (document_id,))

    def get_statistics(self) -> Dict:
        query = """
            SELECT
                COUNT(*) as total_documents,
                COALESCE(SUM(chunks), 0) as total_chunks,
                SUM(CASE WHEN status = 'indexed' THEN 1 ELSE 0 END) as indexed_documents,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_documents,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_documents,
                COALESCE(SUM(retrieval_count), 0) as total_retrievals
            FROM knowledge_documents
        """
        result = self._execute_query(query, fetch_one=True)
        return dict(result) if result else {
            'total_documents': 0,
            'total_chunks': 0,
            'indexed_documents': 0,
            'failed_documents': 0,
            'pending_documents': 0,
            'total_retrievals': 0
        }
