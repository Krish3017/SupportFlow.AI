from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EmailStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    FAILED = "error"

class EmailResponse(BaseModel):
    id: int
    gmail_message_id: Optional[str] = None
    sender_email: str
    subject: str
    body: str
    status: EmailStatus
    ai_response: Optional[str] = None
    created_at: datetime
    ticket_id: Optional[str] = None

class EmailDetailResponse(EmailResponse):
    linked_ticket: Optional[dict] = None

class EmailListResponse(BaseModel):
    emails: List[EmailResponse]
    total: int
    page: int
    limit: int
    pages: int

class ReplyRequest(BaseModel):
    to: str
    subject: str
    body: str

class ReplyResponse(BaseModel):
    success: bool
    message: str
