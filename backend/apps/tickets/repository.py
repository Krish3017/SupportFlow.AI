from typing import Optional, List, Dict, Tuple
from repositories.base import BaseRepository
from core.logging_config import get_logger
from core.errors import NotFoundError
from datetime import datetime

logger = get_logger(__name__)


class TicketRepository(BaseRepository):

    def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        channel: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:

        query = """
            SELECT
                t.id,
                t.conversation_id,
                t.contact_id,
                t.subject,
                t.priority,
                t.status,
                t.assignee,
                t.escalation_reason,
                t.created_at,
                t.updated_at,
                t.resolved_at,
                c.channel as conversation_channel,
                cu.email as customer_email,
                cu.name as customer_name
            FROM tickets t
            LEFT JOIN conversations c ON c.id = t.conversation_id
            LEFT JOIN customers cu ON cu.id = t.contact_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND t.status = ?"
            params.append(status)
        if priority:
            query += " AND t.priority = ?"
            params.append(priority)
        if channel:
            query += " AND c.channel = ?"
            params.append(channel)
        if search:
            query += " AND t.subject LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        tickets = self._execute_query(query, tuple(params), fetch_all=True)

        count_query = "SELECT COUNT(*) as count FROM tickets WHERE 1=1"
        count_params = []
        if status:
            count_query += " AND status = ?"
            count_params.append(status)
        if priority:
            count_query += " AND priority = ?"
            count_params.append(priority)

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return tickets or [], total

    def get_ticket(self, ticket_id: str) -> Dict:
        query = """
            SELECT
                t.*,
                c.channel as conversation_channel,
                cu.email as customer_email,
                cu.name as customer_name,
                (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = t.conversation_id) as message_count
            FROM tickets t
            LEFT JOIN conversations c ON c.id = t.conversation_id
            LEFT JOIN customers cu ON cu.id = t.contact_id
            WHERE t.id = ?
        """
        ticket = self._execute_query(query, (ticket_id,), fetch_one=True)

        if not ticket:
            raise NotFoundError(resource="Ticket", identifier=ticket_id)

        return ticket

    def update_status(self, ticket_id: str, status: str) -> None:
        self.get_ticket(ticket_id)
        now = datetime.utcnow().isoformat()

        query = "UPDATE tickets SET status = ?, updated_at = ?"
        params = [status, now]

        if status == "resolved":
            query += ", resolved_at = ?"
            params.append(now)

        query += " WHERE id = ?"
        params.append(ticket_id)

        self._execute_query(query, tuple(params))
