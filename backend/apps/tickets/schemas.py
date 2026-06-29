"""
Ticket Module Schemas
Pydantic models for ticket-related requests/responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ═══════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════

class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Status(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Channel(str, Enum):
    EMAIL = "email"
    CHAT = "chat"
    TELEGRAM = "telegram"

# ═══════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════

class TicketListQuery(BaseModel):
    """Query parameters for listing tickets"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=100)
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    channel: Optional[Channel] = None
    search: Optional[str] = None

class UpdateTicketStatusRequest(BaseModel):
    """Request body for updating ticket status"""
    status: Status

# ═══════════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class TicketCustomer(BaseModel):
    """Customer summary in ticket response"""
    id: str
    name: Optional[str] = None
    email: str

class TicketResponse(BaseModel):
    """Basic ticket information"""
    id: str
    subject: str
    customer: TicketCustomer
    priority: Priority
    status: Status
    channel: Channel
    sentiment: Optional[Sentiment] = None
    intent: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    current_agent: Optional[str] = None
    time_elapsed: int = 0

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    """Message in ticket conversation"""
    id: int
    role: str
    content: str
    timestamp: datetime
    agent_type: Optional[str] = None

class ExecutionStepResponse(BaseModel):
    """Agent execution step"""
    id: str
    agent_name: str
    status: str
    latency: Optional[float] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error: Optional[str] = None

class TicketDetailResponse(TicketResponse):
    """Detailed ticket with conversation and execution trace"""
    messages: List[MessageResponse] = []
    executions: List[ExecutionStepResponse] = []
    total_latency: float = 0.0
    total_cost: float = 0.0

class TicketListResponse(BaseModel):
    """Paginated ticket list"""
    tickets: List[TicketResponse]
    total: int
    page: int
    limit: int
    pages: int
