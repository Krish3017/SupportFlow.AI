from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ActivityType(str, Enum):
    SYSTEM = "system"
    AGENT = "agent"
    EMAIL = "email"
    SECURITY = "security"
    TICKET = "ticket"
    CUSTOMER = "customer"
    CONVERSATION = "conversation"
    TELEGRAM = "telegram"
    KNOWLEDGE = "knowledge"
    CHAT = "chat"

class ActivityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ActivityResponse(BaseModel):
    id: int
    type: ActivityType
    level: ActivityLevel
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ActivityListResponse(BaseModel):
    activities: List[ActivityResponse]
    total: int
    page: int
    limit: int
    pages: int
