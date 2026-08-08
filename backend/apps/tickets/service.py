from typing import Optional
from .repository import TicketRepository
from .schemas import (
    TicketResponse,
    TicketDetailResponse,
    TicketListResponse,
    TicketCustomer,
    Channel,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


def _safe_channel(raw: Optional[str]) -> Optional[Channel]:
    """Convert raw channel string to Channel enum, returning None for unknown values."""
    if not raw:
        return None
    try:
        return Channel(raw.lower())
    except ValueError:
        return None


class TicketService:

    def __init__(self):
        self.repository = TicketRepository()

    def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        channel: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> TicketListResponse:

        offset = (page - 1) * limit

        tickets_data, total = self.repository.list_tickets(
            status=status,
            priority=priority,
            channel=channel,
            search=search,
            limit=limit,
            offset=offset
        )

        tickets = [self._to_response(t) for t in tickets_data]

        return TicketListResponse(
            tickets=tickets,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0
        )

    def get_ticket_detail(self, ticket_id: str) -> TicketDetailResponse:
        ticket_data = self.repository.get_ticket(ticket_id)

        return TicketDetailResponse(
            id=ticket_data['id'],
            subject=ticket_data['subject'],
            conversation_id=ticket_data['conversation_id'],
            customer=TicketCustomer(
                id=ticket_data['contact_id'],
                email=ticket_data.get('customer_email', 'unknown'),
                name=ticket_data.get('customer_name')
            ),
            priority=ticket_data['priority'],
            status=ticket_data['status'],
            channel=_safe_channel(ticket_data.get('conversation_channel')),
            created_at=ticket_data['created_at'],
            updated_at=ticket_data['updated_at'],
            assignee=ticket_data.get('assignee'),
            escalation_reason=ticket_data.get('escalation_reason'),
            resolved_at=ticket_data.get('resolved_at'),
            message_count=ticket_data.get('message_count', 0)
        )

    def update_ticket_status(self, ticket_id: str, status: str) -> None:
        self.repository.update_status(ticket_id, status)

    def _to_response(self, data: dict) -> TicketResponse:
        return TicketResponse(
            id=data['id'],
            subject=data['subject'],
            conversation_id=data['conversation_id'],
            customer=TicketCustomer(
                id=data['contact_id'],
                email=data.get('customer_email', 'unknown'),
                name=data.get('customer_name')
            ),
            priority=data['priority'],
            status=data['status'],
            channel=_safe_channel(data.get('conversation_channel')),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            assignee=data.get('assignee'),
            escalation_reason=data.get('escalation_reason')
        )
