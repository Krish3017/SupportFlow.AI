from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CustomerTier(str, Enum):
    VIP = "vip"
    STANDARD = "standard"
    NEW = "new"

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class CustomerResponse(BaseModel):
    id: str
    name: Optional[str] = None
    email: str
    tier: CustomerTier
    sentiment: Sentiment
    total_tickets: int = 0
    resolved_tickets: int = 0
    avg_response_time: float = 0.0
    interaction_frequency: Optional[str] = None
    last_interaction: Optional[datetime] = None
    joined_date: datetime
    risk_score: int = 0
    lifetime_value: float = 0.0
    tags: List[str] = []

class TicketSummary(BaseModel):
    id: str
    subject: str
    status: str
    priority: str
    created_at: datetime

class ConversationSummary(BaseModel):
    id: str
    channel: str
    message_count: int
    started_at: datetime

class CustomerDetailResponse(CustomerResponse):
    tickets: List[TicketSummary] = []
    conversations: List[ConversationSummary] = []
    open_tickets: int = 0
    escalated_tickets: int = 0

class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int
    page: int
    limit: int
    pages: int
