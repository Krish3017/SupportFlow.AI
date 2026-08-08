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
                c.id,
                c.contact_id as customer_id,
                c.channel,
                c.status,
                c.subject,
                c.started_at,
                c.updated_at,
                c.resolved_at,
                cu.email as customer_email,
                cu.name as customer_name,
                (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count,
                (SELECT t.id FROM tickets t WHERE t.conversation_id = c.id LIMIT 1) as ticket_id
            FROM conversations c
            LEFT JOIN customers cu ON cu.id = c.contact_id
            WHERE 1=1
        """

        params = []

        if customer_id:
            query += " AND c.contact_id = ?"
            params.append(customer_id)

        if channel:
            query += " AND c.channel = ?"
            params.append(channel)

        if status:
            query += " AND c.status = ?"
            params.append(status)

        if ticket_id:
            query += " AND EXISTS (SELECT 1 FROM tickets t WHERE t.conversation_id = c.id AND t.id = ?)"
            params.append(ticket_id)

        if search:
            query += " AND (c.subject LIKE ? OR EXISTS (SELECT 1 FROM messages m WHERE m.conversation_id = c.id AND m.content LIKE ?))"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY c.updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        conversations = self._execute_query(query, tuple(params), fetch_all=True)

        count_query = "SELECT COUNT(*) as count FROM conversations WHERE 1=1"
        count_params = []

        if customer_id:
            count_query += " AND contact_id = ?"
            count_params.append(customer_id)
        if channel:
            count_query += " AND channel = ?"
            count_params.append(channel)
        if status:
            count_query += " AND status = ?"
            count_params.append(status)

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return conversations or [], total

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        query = """
            SELECT
                c.id,
                c.contact_id as customer_id,
                c.channel,
                c.status,
                c.subject,
                c.started_at,
                c.updated_at,
                c.resolved_at,
                c.closed_at,
                c.session_token,
                cu.email as customer_email,
                cu.name as customer_name,
                (SELECT t.id FROM tickets t WHERE t.conversation_id = c.id LIMIT 1) as ticket_id
            FROM conversations c
            LEFT JOIN customers cu ON cu.id = c.contact_id
            WHERE c.id = ?
        """

        conversation = self._execute_query(query, (conversation_id,), fetch_one=True)

        if not conversation:
            raise NotFoundError(resource="Conversation", identifier=conversation_id)

        return conversation

    def get_messages(self, conversation_id: str) -> List[Dict]:
        query = """
            SELECT id, conversation_id, role, content, timestamp, execution_id
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """
        messages = self._execute_query(query, (conversation_id,), fetch_all=True)
        return messages or []

    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        search_query = """
            SELECT
                c.id,
                c.contact_id as customer_id,
                c.channel,
                c.status,
                c.subject,
                c.started_at,
                c.updated_at,
                cu.email as customer_email,
                cu.name as customer_name,
                (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count,
                (SELECT t.id FROM tickets t WHERE t.conversation_id = c.id LIMIT 1) as ticket_id
            FROM conversations c
            LEFT JOIN customers cu ON cu.id = c.contact_id
            WHERE c.subject LIKE ?
               OR EXISTS (SELECT 1 FROM messages m WHERE m.conversation_id = c.id AND m.content LIKE ?)
            ORDER BY c.updated_at DESC
            LIMIT ?
        """

        results = self._execute_query(search_query, (f"%{query}%", f"%{query}%", limit), fetch_all=True)
        return results or []
