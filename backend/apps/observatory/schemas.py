from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AgentStatusEnum(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"

class ExecutionStatusEnum(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"

class AgentHealthResponse(BaseModel):
    id: str
    name: str
    status: AgentStatusEnum
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_latency: float
    last_execution: Optional[datetime] = None
    error_count: int

class AgentDetailResponse(AgentHealthResponse):
    recent_errors: List[str] = []
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    success_rate: float = 0.0

class ExecutionStepResponse(BaseModel):
    agent_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: float = 0.0
    status: ExecutionStatusEnum
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    error: Optional[str] = None
    sequence_order: int

class ExecutionResponse(BaseModel):
    id: str
    ticket_id: str
    customer_id: Optional[str] = None
    session_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_duration: float = 0.0
    status: ExecutionStatusEnum
    step_count: int
    intent: Optional[str] = None
    priority: Optional[str] = None

class ExecutionDetailResponse(ExecutionResponse):
    steps: List[ExecutionStepResponse] = []

class ExecutionListResponse(BaseModel):
    executions: List[ExecutionResponse]
    total: int
    page: int
    limit: int
    pages: int

class AgentListResponse(BaseModel):
    agents: List[AgentHealthResponse]
