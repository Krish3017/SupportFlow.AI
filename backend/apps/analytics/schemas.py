from pydantic import BaseModel
from typing import List, Dict, Any

class MetricValue(BaseModel):
    label: str
    value: float
    change: float = 0.0
    trend: str = "stable"

class OverviewResponse(BaseModel):
    tickets: Dict[str, Any]
    customers: Dict[str, Any]
    agents: Dict[str, Any]
    knowledge: Dict[str, Any]
    conversations: Dict[str, Any]

class TicketAnalyticsResponse(BaseModel):
    total: int
    open: int
    resolved: int
    escalated: int
    avg_resolution_time: float
    by_priority: List[Dict[str, Any]]
    by_channel: List[Dict[str, Any]]
    trend: List[Dict[str, Any]]

class CustomerAnalyticsResponse(BaseModel):
    total: int
    active: int
    new: int
    by_tier: List[Dict[str, Any]]
    by_sentiment: List[Dict[str, Any]]

class AgentAnalyticsResponse(BaseModel):
    total_executions: int
    success_rate: float
    avg_latency: float
    failed_executions: int
    by_agent: List[Dict[str, Any]]

class KnowledgeAnalyticsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_retrievals: int
    indexed: int
    failed: int
