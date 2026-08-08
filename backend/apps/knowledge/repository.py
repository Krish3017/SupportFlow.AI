import os
import json
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from repositories.base import BaseRepository
from core.errors import NotFoundError
from core.logging_config import get_logger

logger = get_logger(__name__)

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

        query = """
            SELECT
                id,
                title,
                type,
                status,
                chunks_count as chunks,
                retrieval_count,
                updated_at as last_updated,
                size_bytes,
                file_path,
                metadata
            FROM knowledge_documents
            WHERE 1=1
        """
        params = []

        if doc_type:
            query += " AND type = %s"
            params.append(doc_type)

        if status:
            query += " AND status = %s"
            params.append(status)

        if search:
            query += " AND title ILIKE %s"
            params.append(f"%{search}%")

        query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        documents = self._execute_query(query, tuple(params), fetch_all=True)

        count_query = "SELECT COUNT(*) as count FROM knowledge_documents WHERE 1=1"
        count_params = []

        if doc_type:
            count_query += " AND type = %s"
            count_params.append(doc_type)
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        if search:
            count_query += " AND title ILIKE %s"
            count_params.append(f"%{search}%")

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return documents or [], total

    def get_document(self, document_id: str) -> Dict:
        query = """
            SELECT
                id,
                title,
                type,
                status,
                chunks_count as chunks,
                retrieval_count,
                updated_at as last_updated,
                created_at,
                size_bytes,
                file_path,
                metadata
            FROM knowledge_documents
            WHERE id = %s
        """
        doc = self._execute_query(query, (document_id,), fetch_one=True)

        if not doc:
            raise NotFoundError(resource="Document", identifier=document_id)

        return doc

    def create_document(self, doc_data: dict) -> str:
        query = """
            INSERT INTO knowledge_documents
            (id, title, type, status, chunks_count, retrieval_count, size_bytes, file_path, metadata, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                type = EXCLUDED.type,
                status = EXCLUDED.status,
                chunks_count = EXCLUDED.chunks_count,
                size_bytes = EXCLUDED.size_bytes,
                file_path = EXCLUDED.file_path,
                metadata = EXCLUDED.metadata,
                updated_at = EXCLUDED.updated_at
        """
        now = doc_data.get('last_updated') or datetime.utcnow().isoformat()
        meta_json = json.dumps(doc_data.get('metadata', {}))

        self._execute_query(query, (
            doc_data['id'],
            doc_data['title'],
            doc_data['type'],
            doc_data.get('status', 'pending'),
            doc_data.get('chunks', doc_data.get('chunks_count', 0)),
            doc_data.get('retrieval_count', 0),
            doc_data.get('size_bytes', 0),
            doc_data.get('file_path'),
            meta_json,
            now,
            now
        ))
        return doc_data['id']

    def update_document_status(self, document_id: str, status: str, chunks_count: Optional[int] = None) -> None:
        now = datetime.utcnow().isoformat()
        if chunks_count is not None:
            query = "UPDATE knowledge_documents SET status = %s, chunks_count = %s, updated_at = %s WHERE id = %s"
            self._execute_query(query, (status, chunks_count, now, document_id))
        else:
            query = "UPDATE knowledge_documents SET status = %s, updated_at = %s WHERE id = %s"
            self._execute_query(query, (status, now, document_id))

    def replace_document_chunks(self, document_id: str, chunks_data: List[dict]) -> None:
        """Idempotently replace all chunks for a document inside a transaction."""
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM supportflow.knowledge_chunks WHERE document_id = %s", (document_id,))

                insert_sql = """
                    INSERT INTO supportflow.knowledge_chunks
                    (id, document_id, chunk_index, content, token_count, embedding, metadata, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s::vector, %s::jsonb, %s)
                """

                for idx, c in enumerate(chunks_data):
                    chunk_id = c.get('id') or f"{document_id}#chunk_{idx}"
                    vec_str = '[' + ','.join(str(f) for f in c['embedding']) + ']'
                    meta_json = json.dumps(c.get('metadata', {}))

                    cur.execute(insert_sql, (
                        chunk_id,
                        document_id,
                        idx,
                        c['content'],
                        c.get('token_count', len(c['content'])),
                        vec_str,
                        meta_json,
                        now
                    ))

                cur.execute(
                    "UPDATE supportflow.knowledge_documents SET status = 'indexed', chunks_count = %s, updated_at = %s WHERE id = %s",
                    (len(chunks_data), now, document_id)
                )

    def delete_document_chunks(self, document_id: str) -> None:
        query = "DELETE FROM knowledge_chunks WHERE document_id = %s"
        self._execute_query(query, (document_id,))

    def vector_similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        doc_type: Optional[str] = None
    ) -> List[Dict]:
        vec_str = '[' + ','.join(str(f) for f in query_embedding) + ']'

        query = """
            SELECT
                c.id AS chunk_id,
                c.document_id,
                c.chunk_index,
                c.content,
                c.metadata AS chunk_metadata,
                d.title AS document_title,
                d.type AS document_type,
                1 - (c.embedding <=> %s::vector) AS similarity_score
            FROM supportflow.knowledge_chunks c
            JOIN supportflow.knowledge_documents d ON d.id = c.document_id
            WHERE d.status = 'indexed'
        """
        params = [vec_str]

        if doc_type:
            query += " AND d.type = %s"
            params.append(doc_type)

        query += " ORDER BY c.embedding <=> %s::vector ASC LIMIT %s"
        params.extend([vec_str, top_k])

        results = self._execute_query(query, tuple(params), fetch_all=True)
        return results or []

    def retrieve_document_chunks(self, document_id: str) -> List[Dict]:
        query = """
            SELECT id, document_id, chunk_index, content, token_count, created_at
            FROM knowledge_chunks
            WHERE document_id = %s
            ORDER BY chunk_index ASC
        """
        chunks = self._execute_query(query, (document_id,), fetch_all=True)
        return chunks or []

    def delete_document(self, document_id: str) -> None:
        self.get_document(document_id)
        query = "DELETE FROM knowledge_documents WHERE id = %s"
        self._execute_query(query, (document_id,))
        logger.info(f"Deleted document {document_id}")

    def increment_retrieval_count(self, document_id: str) -> None:
        query = "UPDATE knowledge_documents SET retrieval_count = retrieval_count + 1 WHERE id = %s"
        self._execute_query(query, (document_id,))

    def get_statistics(self) -> Dict:
        query = """
            SELECT
                COUNT(*) as total_documents,
                COALESCE(SUM(chunks_count), 0) as total_chunks,
                COALESCE(SUM(CASE WHEN status = 'indexed' THEN 1 ELSE 0 END), 0) as indexed_documents,
                COALESCE(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END), 0) as failed_documents,
                COALESCE(SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END), 0) as pending_documents,
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
