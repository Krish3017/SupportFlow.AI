from typing import Optional, List
from .repository import CustomerRepository
from .schemas import (
    CustomerResponse,
    CustomerDetailResponse,
    CustomerListResponse,
    TicketSummary,
    ConversationSummary,
    CustomerTier,
    Sentiment
)
from core.logging_config import get_logger

logger = get_logger(__name__)

class CustomerService:

    def __init__(self):
        self.repository = CustomerRepository()

    def list_customers(
        self,
        tier: Optional[str] = None,
        sentiment: Optional[str] = None,
        min_risk_score: Optional[int] = None,
        max_risk_score: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> CustomerListResponse:

        offset = (page - 1) * limit

        customers_data, total = self.repository.list_customers(
            tier=tier,
            sentiment=sentiment,
            min_risk_score=min_risk_score,
            max_risk_score=max_risk_score,
            search=search,
            limit=limit,
            offset=offset
        )

        customers = [self._to_response(c) for c in customers_data]

        return CustomerListResponse(
            customers=customers,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0
        )

    def get_customer_detail(self, customer_id: str) -> CustomerDetailResponse:
        customer_data = self.repository.get_customer(customer_id)
        stats = self.repository.get_customer_stats(customer_id)

        tickets_data = self.repository.get_customer_tickets(customer_id)
        tickets = [
            TicketSummary(
                id=t['id'],
                subject=t['subject'],
                status=t['status'],
                priority=t['priority'],
                created_at=t['created_at']
            )
            for t in tickets_data
        ]

        conversations_data = self.repository.get_customer_conversations(customer_id)
        conversations = [
            ConversationSummary(
                id=str(c['id']),
                channel=c.get('channel', 'chat'),
                message_count=c.get('message_count', 0),
                started_at=c['started_at']
            )
            for c in conversations_data
        ]

        return CustomerDetailResponse(
            id=customer_data['id'],
            name=customer_data.get('name'),
            email=customer_data['email'],
            tier=CustomerTier(customer_data.get('tier', 'standard')),
            sentiment=Sentiment(customer_data.get('sentiment', 'neutral')),
            total_tickets=stats.get('total_tickets', 0),
            resolved_tickets=stats.get('resolved_conversations', 0),
            avg_response_time=customer_data.get('avg_response_time', 0.0),
            interaction_frequency=customer_data.get('interaction_frequency'),
            last_interaction=customer_data.get('last_interaction'),
            joined_date=customer_data['joined_date'],
            risk_score=customer_data.get('risk_score', 0),
            lifetime_value=customer_data.get('lifetime_value', 0.0),
            tags=customer_data.get('tags', '').split(',') if customer_data.get('tags') else [],
            tickets=tickets,
            conversations=conversations,
            open_tickets=stats.get('open_tickets', 0),
            escalated_tickets=0
        )

    def get_customer_tickets(self, customer_id: str) -> List[TicketSummary]:
        self.repository.get_customer(customer_id)  # Verify exists
        tickets_data = self.repository.get_customer_tickets(customer_id)

        return [
            TicketSummary(
                id=t['id'],
                subject=t['subject'],
                status=t['status'],
                priority=t['priority'],
                created_at=t['created_at']
            )
            for t in tickets_data
        ]

    def get_customer_conversations(self, customer_id: str) -> List[ConversationSummary]:
        self.repository.get_customer(customer_id)  # Verify exists
        conversations_data = self.repository.get_customer_conversations(customer_id)

        return [
            ConversationSummary(
                id=str(c['id']),
                channel=c.get('channel', 'chat'),
                message_count=c.get('message_count', 0),
                started_at=c['started_at']
            )
            for c in conversations_data
        ]

    def search_customers(self, query: str, limit: int = 20) -> List[CustomerResponse]:
        results = self.repository.search_customers(query, limit)
        return [self._to_response(r) for r in results]

    def _to_response(self, data: dict) -> CustomerResponse:
        return CustomerResponse(
            id=data['id'],
            name=data.get('name'),
            email=data['email'],
            tier=CustomerTier(data.get('tier', 'standard')),
            sentiment=Sentiment(data.get('sentiment', 'neutral')),
            total_tickets=data.get('total_tickets', 0),
            resolved_tickets=data.get('resolved_tickets', 0),
            avg_response_time=data.get('avg_response_time', 0.0),
            interaction_frequency=data.get('interaction_frequency'),
            last_interaction=data.get('last_interaction'),
            joined_date=data['joined_date'],
            risk_score=data.get('risk_score', 0),
            lifetime_value=data.get('lifetime_value', 0.0),
            tags=data.get('tags', '').split(',') if data.get('tags') else []
        )
