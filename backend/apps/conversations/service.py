from typing import Optional, List
from .repository import ConversationRepository
from .schemas import (
    ConversationResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    CustomerSummary,
    MessageResponse,
    Channel,
    ConversationStatus
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class ConversationService:

    def __init__(self):
        self.repository = ConversationRepository()

    def list_conversations(
        self,
        customer_id: Optional[str] = None,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        ticket_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> ConversationListResponse:

        offset = (page - 1) * limit

        conversations_data, total = self.repository.list_conversations(
            customer_id=customer_id,
            channel=channel,
            status=status,
            ticket_id=ticket_id,
            search=search,
            limit=limit,
            offset=offset
        )

        conversations = [self._to_response(c) for c in conversations_data]

        return ConversationListResponse(
            conversations=conversations,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0
        )

    def get_conversation_detail(self, conversation_id: str) -> ConversationDetailResponse:
        conversation_data = self.repository.get_conversation(conversation_id)
        messages_data = self.repository.get_messages(conversation_id)

        messages = [
            MessageResponse(
                id=m['id'],
                role=m['role'],
                content=m['content'],
                timestamp=m['timestamp'],
                execution_id=m.get('execution_id')
            )
            for m in messages_data
        ]

        channel = self._safe_channel(conversation_data.get('channel', 'chat'))
        status = self._safe_status(conversation_data.get('status', 'active'))

        return ConversationDetailResponse(
            id=conversation_data['id'],
            customer=CustomerSummary(
                id=conversation_data.get('customer_id', 'anonymous'),
                email=conversation_data.get('customer_email', 'unknown@example.com'),
                name=conversation_data.get('customer_name')
            ),
            channel=channel,
            status=status,
            subject=conversation_data.get('subject'),
            ticket_id=conversation_data.get('ticket_id'),
            message_count=len(messages),
            started_at=conversation_data['started_at'],
            updated_at=conversation_data['updated_at'],
            resolved_at=conversation_data.get('resolved_at'),
            messages=messages,
            session_id=conversation_data.get('session_token')
        )

    def get_messages(self, conversation_id: str) -> List[MessageResponse]:
        messages_data = self.repository.get_messages(conversation_id)

        return [
            MessageResponse(
                id=m['id'],
                role=m['role'],
                content=m['content'],
                timestamp=m['timestamp'],
                execution_id=m.get('execution_id')
            )
            for m in messages_data
        ]

    def search_conversations(self, query: str, limit: int = 20) -> List[ConversationResponse]:
        results = self.repository.search_conversations(query, limit)
        return [self._to_response(r) for r in results]

    def _to_response(self, data: dict) -> ConversationResponse:
        channel = self._safe_channel(data.get('channel', 'chat'))
        status = self._safe_status(data.get('status', 'active'))

        return ConversationResponse(
            id=data['id'],
            customer=CustomerSummary(
                id=data.get('customer_id', 'anonymous'),
                email=data.get('customer_email', 'unknown@example.com'),
                name=data.get('customer_name')
            ),
            channel=channel,
            status=status,
            subject=data.get('subject'),
            ticket_id=data.get('ticket_id'),
            message_count=data.get('message_count', 0),
            started_at=data.get('started_at'),
            updated_at=data.get('updated_at', data.get('started_at'))
        )

    def _safe_status(self, status: str) -> ConversationStatus:
        try:
            return ConversationStatus(status)
        except ValueError:
            return ConversationStatus.ACTIVE

    def _safe_channel(self, channel: str) -> Channel:
        try:
            return Channel(channel)
        except ValueError:
            return Channel.CHAT
