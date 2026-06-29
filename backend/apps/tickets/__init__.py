"""
Ticket Module
Complete ticket management feature

Exports:
- router: FastAPI router with ticket endpoints
- TicketService: Business logic layer
- TicketRepository: Data access layer
- Schemas: All request/response models
"""
from .router import router
from .service import TicketService
from .repository import TicketRepository

__all__ = ["router", "TicketService", "TicketRepository"]
