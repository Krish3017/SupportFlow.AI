from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class Channel(str, Enum):
    EMAIL = "email"
    CHAT = "chat"
    TELEGRAM = "telegram"


class TicketListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=100)
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    channel: Optional[Channel] = None
    search: Optional[str] = None


class UpdateTicketStatusRequest(BaseModel):
    status: Status


class TicketCustomer(BaseModel):
    id: str
    name: Optional[str] = None
    email: str


class TicketResponse(BaseModel):
    id: str
    subject: str
    conversation_id: str
    customer: TicketCustomer
    priority: Priority
    status: Status
    # Actual channel from the linked conversation — never defaults to "web"
    channel: Optional[Channel] = None
    created_at: datetime
    updated_at: datetime
    assignee: Optional[str] = None
    escalation_reason: Optional[str] = None


class TicketDetailResponse(TicketResponse):
    resolved_at: Optional[datetime] = None
    message_count: int = 0


class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    page: int
    limit: int
    pages: int
