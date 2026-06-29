from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Channel(str, Enum):
    EMAIL = "email"
    CHAT = "chat"
    TELEGRAM = "telegram"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    WAITING = "waiting"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime
    execution_id: Optional[str] = None


class CustomerSummary(BaseModel):
    id: str
    email: str
    name: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    customer: CustomerSummary
    channel: Channel
    status: ConversationStatus
    subject: Optional[str] = None
    ticket_id: Optional[str] = None
    message_count: int
    started_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse]
    session_id: Optional[str] = None
    resolved_at: Optional[datetime] = None


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    limit: int
    pages: int
