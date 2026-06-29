"""
Ticket Repository
Data access layer for tickets
"""
from typing import Optional, List, Dict, Any, Tuple
from repositories.base import BaseRepository
from core.logging_config import get_logger
from core.errors import NotFoundError
from utils.filtering import QueryBuilder, SortOrder

logger = get_logger(__name__)

class TicketRepository(BaseRepository):
    """Repository for ticket data operations"""

    def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        channel: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:
        """
        List tickets with filters and pagination

        Returns:
            Tuple of (ticket list, total count)
        """
        # Build filtered query
        builder = QueryBuilder("SELECT * FROM tickets")

        if status:
            builder.add_filter("status", status)
        if priority:
            builder.add_filter("priority", priority)
        if channel:
            builder.add_filter("channel", channel)
        if search:
            builder.add_like_filter("subject", search)

        builder.add_sort("created_at", SortOrder.DESC)
        builder.add_pagination(limit, offset)

        query, params = builder.build()
        tickets = self._execute_query(query, tuple(params), fetch_all=True)

        # Get total count
        count_builder = QueryBuilder("SELECT COUNT(*) as count FROM tickets")
        if status:
            count_builder.add_filter("status", status)
        if priority:
            count_builder.add_filter("priority", priority)
        if channel:
            count_builder.add_filter("channel", channel)
        if search:
            count_builder.add_like_filter("subject", search)

        count_query, count_params = count_builder.build()
        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return tickets, total

    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get ticket by ID"""
        query = "SELECT * FROM tickets WHERE id = ?"
        ticket = self._execute_query(query, (ticket_id,), fetch_one=True)

        if not ticket:
            raise NotFoundError(resource="Ticket", identifier=ticket_id)

        return ticket

    def update_status(self, ticket_id: str, status: str) -> None:
        """Update ticket status"""
        # Verify ticket exists
        self.get_ticket(ticket_id)

        query = "UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?"
        from datetime import datetime
        self._execute_query(query, (status, datetime.now().isoformat(), ticket_id))

        logger.info(f"Updated ticket {ticket_id} status to {status}")

    def get_messages(self, ticket_id: str) -> List[Dict]:
        """Get all messages for a ticket"""
        query = "SELECT * FROM messages WHERE ticket_id = ? ORDER BY timestamp"
        messages = self._execute_query(query, (ticket_id,), fetch_all=True)
        return messages or []

    def get_executions(self, ticket_id: str) -> List[Dict]:
        """Get all agent executions for a ticket"""
        query = "SELECT * FROM agent_executions WHERE ticket_id = ? ORDER BY sequence_order"
        executions = self._execute_query(query, (ticket_id,), fetch_all=True)
        return executions or []
