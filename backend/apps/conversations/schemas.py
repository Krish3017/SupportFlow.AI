from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Channel(str, Enum):
    EMAIL = "email"
    CHAT = "chat"
    TELEGRAM = "telegram"

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime
    agent_type: Optional[str] = None

class CustomerSummary(BaseModel):
    id: str
    email: str
    name: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    customer: CustomerSummary
    channel: Channel
    status: ConversationStatus
    ticket_id: Optional[str] = None
    message_count: int
    started_at: datetime
    updated_at: datetime

class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse]
    session_id: Optional[str] = None

class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    limit: int
    pages: int
