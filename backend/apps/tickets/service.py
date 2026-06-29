"""
Ticket Service
Business logic for ticket operations
"""
from typing import List, Optional
from .repository import TicketRepository
from .schemas import (
    TicketResponse,
    TicketDetailResponse,
    TicketListResponse,
    TicketCustomer,
    MessageResponse,
    ExecutionStepResponse
)
from core.logging_config import get_logger

logger = get_logger(__name__)

class TicketService:
    """Service layer for ticket business logic"""

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
        """
        List tickets with filters and pagination

        Args:
            status: Filter by status
            priority: Filter by priority
            channel: Filter by channel
            search: Search in subject
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            TicketListResponse with tickets and pagination metadata
        """
        offset = (page - 1) * limit

        tickets_data, total = self.repository.list_tickets(
            status=status,
            priority=priority,
            channel=channel,
            search=search,
            limit=limit,
            offset=offset
        )

        # Transform to response DTOs
        tickets = [self._ticket_to_response(t) for t in tickets_data]

        return TicketListResponse(
            tickets=tickets,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0
        )

    def get_ticket_detail(self, ticket_id: str) -> TicketDetailResponse:
        """
        Get detailed ticket information

        Args:
            ticket_id: Ticket ID

        Returns:
            TicketDetailResponse with full conversation and execution trace
        """
        # Get basic ticket data
        ticket_data = self.repository.get_ticket(ticket_id)

        # Get messages
        messages_data = self.repository.get_messages(ticket_id)
        messages = [
            MessageResponse(
                id=m['id'],
                role=m['role'],
                content=m['content'],
                timestamp=m['timestamp'],
                agent_type=m.get('agent_type')
            )
            for m in messages_data
        ]

        # Get agent executions
        executions_data = self.repository.get_executions(ticket_id)
        executions = [
            ExecutionStepResponse(
                id=e['id'],
                agent_name=e['agent_name'],
                status=e['status'],
                latency=e.get('latency'),
                input_data=e.get('input_data'),
                output_data=e.get('output_data'),
                error=e.get('error')
            )
            for e in executions_data
        ]

        # Calculate totals
        total_latency = sum(e.get('latency', 0) or 0 for e in executions_data)
        total_cost = sum(e.get('cost', 0) or 0 for e in executions_data)

        # Build response
        return TicketDetailResponse(
            id=ticket_data['id'],
            subject=ticket_data['subject'],
            customer=TicketCustomer(
                id=ticket_data['customer_id'],
                email=ticket_data.get('customer_id', 'unknown')
            ),
            priority=ticket_data['priority'],
            status=ticket_data['status'],
            channel=ticket_data['channel'],
            sentiment=ticket_data.get('sentiment'),
            intent=ticket_data.get('intent'),
            created_at=ticket_data['created_at'],
            updated_at=ticket_data['updated_at'],
            current_agent=ticket_data.get('current_agent'),
            time_elapsed=ticket_data.get('time_elapsed', 0),
            messages=messages,
            executions=executions,
            total_latency=total_latency,
            total_cost=total_cost
        )

    def update_ticket_status(self, ticket_id: str, status: str) -> None:
        """
        Update ticket status

        Args:
            ticket_id: Ticket ID
            status: New status
        """
        self.repository.update_status(ticket_id, status)
        logger.info(f"Ticket {ticket_id} status updated to {status}")

    def _ticket_to_response(self, ticket_data: dict) -> TicketResponse:
        """Transform DB dict to TicketResponse DTO"""
        return TicketResponse(
            id=ticket_data['id'],
            subject=ticket_data['subject'],
            customer=TicketCustomer(
                id=ticket_data['customer_id'],
                email=ticket_data.get('customer_id', 'unknown')
            ),
            priority=ticket_data['priority'],
            status=ticket_data['status'],
            channel=ticket_data['channel'],
            sentiment=ticket_data.get('sentiment'),
            intent=ticket_data.get('intent'),
            created_at=ticket_data['created_at'],
            updated_at=ticket_data['updated_at'],
            current_agent=ticket_data.get('current_agent'),
            time_elapsed=ticket_data.get('time_elapsed', 0)
        )
