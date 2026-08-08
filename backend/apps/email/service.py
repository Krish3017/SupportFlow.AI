from typing import Optional, List
from .repository import EmailRepository
from .schemas import (
    EmailResponse,
    EmailDetailResponse,
    EmailListResponse,
    EmailStatus,
    LinkedTicket,
    ReplyResponse
)
from services.email_service import EmailService as ResendEmailService
from core.logging_config import get_logger

logger = get_logger(__name__)

class EmailAdminService:

    def __init__(self):
        self.repository = EmailRepository()
        self.resend_service = ResendEmailService()

    def list_emails(
        self,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> EmailListResponse:

        offset = (page - 1) * limit

        emails_data, total = self.repository.list_emails(
            status=status,
            search=search,
            limit=limit,
            offset=offset
        )

        emails = [self._to_response(e) for e in emails_data]

        return EmailListResponse(
            emails=emails,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0
        )

    def get_email_detail(self, email_id: int) -> EmailDetailResponse:
        data = self.repository.get_email(email_id)
        conversation_id = data.get('conversation_id')

        # Only look up a ticket if a conversation exists for this email
        linked_ticket = None
        if conversation_id:
            ticket_row = self.repository.get_linked_ticket(conversation_id)
            if ticket_row:
                linked_ticket = LinkedTicket(
                    id=ticket_row['id'],
                    subject=ticket_row['subject'],
                    status=ticket_row['status'],
                    priority=ticket_row['priority'],
                    created_at=ticket_row['created_at']
                )

        return EmailDetailResponse(
            id=data['id'],
            gmail_message_id=data.get('gmail_message_id'),
            sender_email=data['sender_email'],
            subject=data['subject'],
            body=data['body'],
            status=EmailStatus(data['status']),
            ai_response=data.get('ai_response'),
            created_at=data['created_at'],
            conversation_id=conversation_id,
            linked_ticket=linked_ticket
        )

    def search_emails(self, query: str, limit: int = 20) -> List[EmailResponse]:
        results = self.repository.search_emails(query, limit)
        return [self._to_response(r) for r in results]

    def send_reply(self, to: str, subject: str, body: str) -> ReplyResponse:
        sent = self.resend_service.send_resolution(
            to=to,
            subject=subject,
            ai_response=body
        )

        if sent:
            return ReplyResponse(success=True, message="Reply sent successfully")
        return ReplyResponse(success=False, message="Failed to send reply")

    def retry_email(self, email_id: int) -> ReplyResponse:
        data = self.repository.get_email(email_id)

        if data['status'] != 'error':
            return ReplyResponse(success=False, message="Email is not in failed state")

        self.repository.update_status(email_id, 'pending')
        return ReplyResponse(success=True, message="Email queued for retry")

    def _to_response(self, data: dict) -> EmailResponse:
        return EmailResponse(
            id=data['id'],
            gmail_message_id=data.get('gmail_message_id'),
            sender_email=data['sender_email'],
            subject=data['subject'],
            body=data['body'],
            status=EmailStatus(data['status']),
            ai_response=data.get('ai_response'),
            created_at=data['created_at'],
            conversation_id=data.get('conversation_id')
        )
