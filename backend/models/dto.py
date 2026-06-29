"""
Data Transfer Objects (DTOs) for SupportFlow AI Admin API
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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
    WHATSAPP = "whatsapp"

class CustomerTier(str, Enum):
    VIP = "vip"
    STANDARD = "standard"
    NEW = "new"

class AgentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"

class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"

class ActivityType(str, Enum):
    SYSTEM = "system"
    AGENT = "agent"
    EMAIL = "email"
    SECURITY = "security"

class ActivityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# ═══════════════════════════════════════════════════════════════
# TICKET DTOs
# ═══════════════════════════════════════════════════════════════

class TicketCustomer(BaseModel):
    id: str
    name: Optional[str] = None
    email: str
    avatar: Optional[str] = None

class TicketResponse(BaseModel):
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
    assignee: Optional[str] = None

class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    page: int
    limit: int

class AgentExecutionStep(BaseModel):
    id: str
    agent_id: str
    agent_name: str
    status: ExecutionStatus
    latency: Optional[float] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    cost: float = 0.0
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

class TicketDetailResponse(TicketResponse):
    messages: List[Dict[str, Any]] = []
    executions: List[AgentExecutionStep] = []
    total_latency: float = 0.0
    total_cost: float = 0.0

class UpdateTicketStatusRequest(BaseModel):
    status: Status

# ═══════════════════════════════════════════════════════════════
# CUSTOMER DTOs
# ═══════════════════════════════════════════════════════════════

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
    last_interaction: datetime
    joined_date: datetime
    risk_score: int = 0
    lifetime_value: float = 0.0
    tags: List[str] = []

class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int

class CustomerDetailResponse(CustomerResponse):
    tickets: List[TicketResponse] = []
    sentiment_history: List[Dict[str, Any]] = []

# ═══════════════════════════════════════════════════════════════
# AGENT DTOs
# ═══════════════════════════════════════════════════════════════

class AgentHealthResponse(BaseModel):
    id: str
    name: str
    description: str
    status: AgentStatus
    success_rate: float
    avg_latency: float
    total_executions: int
    failed_executions: int
    last_error: Optional[str] = None
    cost: float

class AgentExecutionResponse(BaseModel):
    id: str
    ticket_id: str
    session_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_latency: float
    total_cost: float
    status: ExecutionStatus
    steps: List[AgentExecutionStep]

# ═══════════════════════════════════════════════════════════════
# CONVERSATION DTOs
# ═══════════════════════════════════════════════════════════════

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime
    agent_type: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    ticket_id: str
    customer_id: str
    channel: Channel
    messages: List[MessageResponse]
    status: Status
    started_at: datetime
    last_message_at: datetime

# ═══════════════════════════════════════════════════════════════
# KNOWLEDGE DTOs
# ═══════════════════════════════════════════════════════════════

class KnowledgeDocumentStatus(str, Enum):
    INDEXED = "indexed"
    PENDING = "pending"
    FAILED = "failed"

class KnowledgeDocumentResponse(BaseModel):
    id: str
    title: str
    type: str
    status: KnowledgeDocumentStatus
    chunks: int
    retrieval_count: int
    last_updated: datetime
    size: str

# ═══════════════════════════════════════════════════════════════
# ANALYTICS DTOs
# ═══════════════════════════════════════════════════════════════

class MetricResponse(BaseModel):
    label: str
    value: float
    change: float
    trend: str  # "up" | "down" | "stable"

class ChartDataPoint(BaseModel):
    label: str
    value: float

class AnalyticsResponse(BaseModel):
    metrics: Dict[str, MetricResponse]
    charts: Dict[str, List[ChartDataPoint]]

# ═══════════════════════════════════════════════════════════════
# ACTIVITY LOG DTOs
# ═══════════════════════════════════════════════════════════════

class ActivityLogResponse(BaseModel):
    id: int
    type: ActivityType
    level: ActivityLevel
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

# ═══════════════════════════════════════════════════════════════
# GENERIC RESPONSE WRAPPERS
# ═══════════════════════════════════════════════════════════════

class SuccessResponse(BaseModel):
    success: bool = True
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
