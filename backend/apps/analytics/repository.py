from repositories.base import BaseRepository
from core.logging_config import get_logger

logger = get_logger(__name__)


class AnalyticsRepository(BaseRepository):

    def get_conversation_overview(self) -> dict:
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'escalated' THEN 1 ELSE 0 END) as escalated
            FROM conversations
        """
        result = self._execute_query(query, fetch_one=True)
        return dict(result) if result else {'total': 0, 'active': 0, 'resolved': 0, 'escalated': 0}

    def get_conversations_by_channel(self) -> list:
        query = """
            SELECT channel, COUNT(*) as count
            FROM conversations
            GROUP BY channel
            ORDER BY count DESC
        """
        return self._execute_query(query, fetch_all=True) or []

    def get_conversation_trend(self) -> list:
        query = """
            SELECT
                DATE(started_at) as date,
                COUNT(*) as count
            FROM conversations
            GROUP BY DATE(started_at)
            ORDER BY date DESC
            LIMIT 30
        """
        return self._execute_query(query, fetch_all=True) or []

    def get_ticket_stats(self) -> dict:
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'escalated' THEN 1 ELSE 0 END) as escalated
            FROM tickets
        """
        result = self._execute_query(query, fetch_one=True)
        return dict(result) if result else {'total': 0, 'open': 0, 'resolved': 0, 'escalated': 0}

    def get_tickets_by_priority(self) -> list:
        query = """
            SELECT priority, COUNT(*) as count
            FROM tickets
            GROUP BY priority
            ORDER BY count DESC
        """
        return self._execute_query(query, fetch_all=True) or []

    def get_customer_stats(self) -> dict:
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN tier = 'standard' THEN 1 ELSE 0 END) as standard_customers
            FROM customers
        """
        result = self._execute_query(query, fetch_one=True)
        return dict(result) if result else {'total': 0, 'standard_customers': 0}

    def get_customers_by_tier(self) -> list:
        query = """
            SELECT tier, COUNT(*) as count
            FROM customers
            GROUP BY tier
        """
        return self._execute_query(query, fetch_all=True) or []

    def get_customers_by_sentiment(self) -> list:
        query = """
            SELECT sentiment, COUNT(*) as count
            FROM customers
            GROUP BY sentiment
        """
        return self._execute_query(query, fetch_all=True) or []

    def get_agent_stats(self) -> dict:
        query = """
            SELECT
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(latency) as avg_latency
            FROM execution_steps
        """
        result = self._execute_query(query, fetch_one=True)
        return dict(result) if result else {'total_executions': 0, 'failed': 0, 'avg_latency': 0}

    def get_agent_stats_by_agent(self) -> list:
        query = """
            SELECT
                agent_id,
                agent_name,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(latency) as avg_latency
            FROM execution_steps
            GROUP BY agent_id
        """
        return self._execute_query(query, fetch_all=True) or []

    def get_knowledge_stats(self) -> dict:
        query = """
            SELECT
                COUNT(*) as total_documents,
                COALESCE(SUM(chunks), 0) as total_chunks,
                COALESCE(SUM(retrieval_count), 0) as total_retrievals,
                COALESCE(SUM(CASE WHEN status = 'indexed' THEN 1 ELSE 0 END), 0) as indexed,
                COALESCE(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END), 0) as failed
            FROM knowledge_documents
        """
        result = self._execute_query(query, fetch_one=True)
        return dict(result) if result else {
            'total_documents': 0, 'total_chunks': 0, 'total_retrievals': 0, 'indexed': 0, 'failed': 0
        }

    def get_execution_stats(self) -> dict:
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(total_duration) as avg_duration
            FROM executions
        """
        result = self._execute_query(query, fetch_one=True)
        return dict(result) if result else {'total': 0, 'completed': 0, 'failed': 0, 'avg_duration': 0}
