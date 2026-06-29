from .repository import AnalyticsRepository
from .schemas import (
    OverviewResponse,
    TicketAnalyticsResponse,
    CustomerAnalyticsResponse,
    AgentAnalyticsResponse,
    KnowledgeAnalyticsResponse
)
from core.logging_config import get_logger

logger = get_logger(__name__)

class AnalyticsService:

    def __init__(self):
        self.repository = AnalyticsRepository()

    def get_overview(self) -> OverviewResponse:
        ticket_stats = self.repository.get_ticket_stats()
        customer_stats = self.repository.get_customer_stats()
        agent_stats = self.repository.get_agent_stats()
        knowledge_stats = self.repository.get_knowledge_stats()
        conversation_stats = self.repository.get_conversation_stats()

        total_exec = agent_stats['total_executions'] or 0
        failed_exec = agent_stats['failed'] or 0
        success_rate = ((total_exec - failed_exec) / total_exec * 100) if total_exec > 0 else 0

        return OverviewResponse(
            tickets={
                "total": ticket_stats['total'],
                "open": ticket_stats['open'],
                "resolved": ticket_stats['resolved'],
                "escalated": ticket_stats['escalated'],
            },
            customers={
                "total": customer_stats['total'],
                "new": customer_stats['new_customers'],
            },
            agents={
                "total_executions": total_exec,
                "success_rate": round(success_rate, 1),
                "avg_latency": round(agent_stats['avg_latency'] or 0, 2),
                "failed": failed_exec,
            },
            knowledge={
                "documents": knowledge_stats['total_documents'],
                "chunks": knowledge_stats['total_chunks'],
                "retrievals": knowledge_stats['total_retrievals'],
            },
            conversations={
                "total": conversation_stats['total'],
                "completed": conversation_stats['completed'],
                "escalated": conversation_stats['escalated'],
            }
        )

    def get_ticket_analytics(self) -> TicketAnalyticsResponse:
        stats = self.repository.get_ticket_stats()
        by_priority = [dict(r) for r in self.repository.get_tickets_by_priority()]
        by_channel = [dict(r) for r in self.repository.get_tickets_by_channel()]
        trend = [dict(r) for r in self.repository.get_ticket_trend()]

        return TicketAnalyticsResponse(
            total=stats['total'],
            open=stats['open'],
            resolved=stats['resolved'],
            escalated=stats['escalated'],
            avg_resolution_time=0.0,
            by_priority=by_priority,
            by_channel=by_channel,
            trend=trend
        )

    def get_customer_analytics(self) -> CustomerAnalyticsResponse:
        stats = self.repository.get_customer_stats()
        by_tier = [dict(r) for r in self.repository.get_customers_by_tier()]
        by_sentiment = [dict(r) for r in self.repository.get_customers_by_sentiment()]

        return CustomerAnalyticsResponse(
            total=stats['total'],
            active=stats['total'],
            new=stats['new_customers'],
            by_tier=by_tier,
            by_sentiment=by_sentiment
        )

    def get_agent_analytics(self) -> AgentAnalyticsResponse:
        stats = self.repository.get_agent_stats()
        by_agent = [dict(r) for r in self.repository.get_agent_stats_by_agent()]

        total = stats['total_executions'] or 0
        failed = stats['failed'] or 0
        success_rate = ((total - failed) / total * 100) if total > 0 else 0

        return AgentAnalyticsResponse(
            total_executions=total,
            success_rate=round(success_rate, 1),
            avg_latency=round(stats['avg_latency'] or 0, 2),
            failed_executions=failed,
            by_agent=by_agent
        )

    def get_knowledge_analytics(self) -> KnowledgeAnalyticsResponse:
        stats = self.repository.get_knowledge_stats()
        return KnowledgeAnalyticsResponse(**stats)
