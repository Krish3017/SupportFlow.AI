from typing import Optional, List, Dict, Tuple
from repositories.base import BaseRepository
from core.errors import NotFoundError
from core.logging_config import get_logger

logger = get_logger(__name__)

class ConversationRepository(BaseRepository):

    def list_conversations(
        self,
        customer_id: Optional[str] = None,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        ticket_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:

        query = """
            SELECT
                t.id,
                t.subject as customer_message,
                t.intent,
                t.sentiment,
                CASE WHEN t.status = 'escalated' THEN 1 ELSE 0 END as escalated,
                t.created_at as timestamp,
                t.id as ticket_id,
                t.customer_id,
                t.channel,
                t.status,
                t.created_at,
                t.updated_at,
                (SELECT COUNT(*) FROM messages m WHERE m.ticket_id = t.id) as message_count
            FROM tickets t
            WHERE 1=1
        """

        params = []

        if customer_id:
            query += " AND t.customer_id = ?"
            params.append(customer_id)

        if channel:
            query += " AND t.channel = ?"
            params.append(channel)

        if status:
            if status == 'active':
                query += " AND t.status IN ('new', 'in_progress')"
            elif status == 'resolved':
                query += " AND t.status = 'resolved'"
            elif status == 'escalated':
                query += " AND t.status = 'escalated'"

        if ticket_id:
            query += " AND t.id = ?"
            params.append(ticket_id)

        if search:
            query += " AND t.subject LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        conversations = self._execute_query(query, tuple(params), fetch_all=True)

        # Count
        count_query = "SELECT COUNT(*) as count FROM tickets WHERE 1=1"
        count_params = []

        if customer_id:
            count_query += " AND customer_id = ?"
            count_params.append(customer_id)
        if channel:
            count_query += " AND channel = ?"
            count_params.append(channel)
        if search:
            count_query += " AND subject LIKE ?"
            count_params.append(f"%{search}%")

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return conversations or [], total

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        query = """
            SELECT
                t.id,
                t.subject as customer_message,
                t.intent,
                t.sentiment,
                CASE WHEN t.status = 'escalated' THEN 1 ELSE 0 END as escalated,
                t.created_at as timestamp,
                t.id as ticket_id,
                t.customer_id,
                t.channel,
                t.status,
                t.created_at,
                t.updated_at
            FROM tickets t
            WHERE t.id = ?
        """

        conversation = self._execute_query(query, (conversation_id,), fetch_one=True)

        if not conversation:
            raise NotFoundError(resource="Conversation", identifier=conversation_id)

        return conversation

    def get_messages(self, conversation_id: str) -> List[Dict]:
        query = "SELECT * FROM messages WHERE ticket_id = ? ORDER BY timestamp"
        messages = self._execute_query(query, (conversation_id,), fetch_all=True)
        return messages or []

    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        search_query = """
            SELECT
                t.id,
                t.subject as customer_message,
                t.intent,
                t.created_at as timestamp,
                t.id as ticket_id,
                t.customer_id,
                t.channel,
                t.status,
                t.updated_at
            FROM tickets t
            WHERE t.subject LIKE ?
            ORDER BY t.created_at DESC
            LIMIT ?
        """

        results = self._execute_query(search_query, (f"%{query}%", limit), fetch_all=True)
        return results or []
