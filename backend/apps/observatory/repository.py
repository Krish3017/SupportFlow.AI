from typing import Optional, List, Dict, Tuple
from repositories.base import BaseRepository
from core.errors import NotFoundError
from core.logging_config import get_logger

logger = get_logger(__name__)

AGENT_NAMES = {
    "intent_agent": "Intent Agent",
    "customer_intelligence_agent": "Customer Intelligence Agent",
    "priority_agent": "Priority Agent",
    "knowledge_agent": "Knowledge Agent",
    "resolution_agent": "Resolution Agent",
    "escalation_agent": "Escalation Agent",
}


class ObservatoryRepository(BaseRepository):

    def get_agent_stats(self) -> List[Dict]:
        query = """
            SELECT
                agent_id,
                agent_name,
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_executions,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_executions,
                AVG(latency) as avg_latency,
                MAX(started_at) as last_execution
            FROM execution_steps
            GROUP BY agent_id, agent_name
            ORDER BY agent_id
        """
        results = self._execute_query(query, fetch_all=True)
        return results or []

    def get_agent_detail(self, agent_name: str) -> Dict:
        stats_query = """
            SELECT
                agent_id,
                agent_name,
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_executions,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_executions,
                AVG(latency) as avg_latency,
                MAX(started_at) as last_execution
            FROM execution_steps
            WHERE agent_id = %s OR agent_name = %s
            GROUP BY agent_id, agent_name
        """
        stats = self._execute_query(stats_query, (agent_name, agent_name), fetch_one=True)

        if not stats:
            raise NotFoundError(resource="Agent", identifier=agent_name)

        errors_query = """
            SELECT error FROM execution_steps
            WHERE agent_id = ? AND status = 'failed' AND error IS NOT NULL
            ORDER BY started_at DESC
            LIMIT 5
        """
        errors = self._execute_query(errors_query, (agent_name,), fetch_all=True)

        latency_query = """
            SELECT latency FROM execution_steps
            WHERE agent_id = ? AND latency IS NOT NULL
            ORDER BY latency
        """
        latencies = self._execute_query(latency_query, (agent_name,), fetch_all=True)

        stats_dict = dict(stats)
        stats_dict['recent_errors'] = [e['error'] for e in (errors or [])]
        stats_dict['latencies'] = [l['latency'] for l in (latencies or [])]

        return stats_dict

    def list_executions(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        ticket_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:

        query = """
            SELECT
                e.id,
                e.conversation_id,
                c.contact_id as customer_id,
                e.message_id,
                e.status,
                e.started_at,
                e.completed_at,
                e.total_duration,
                e.confidence,
                e.intent,
                e.sentiment,
                e.priority,
                e.escalated,
                (SELECT COUNT(*) FROM execution_steps s WHERE s.execution_id = e.id) as step_count
            FROM executions e
            LEFT JOIN conversations c ON c.id = e.conversation_id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND e.status = ?"
            params.append(status)

        if agent_id:
            query += " AND EXISTS (SELECT 1 FROM execution_steps s WHERE s.execution_id = e.id AND s.agent_id = ?)"
            params.append(agent_id)

        if ticket_id:
            query += " AND EXISTS (SELECT 1 FROM tickets t WHERE t.conversation_id = e.conversation_id AND t.id = ?)"
            params.append(ticket_id)

        query += " ORDER BY e.started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        executions = self._execute_query(query, tuple(params), fetch_all=True)

        count_query = "SELECT COUNT(*) as count FROM executions WHERE 1=1"
        count_params = []

        if status:
            count_query += " AND status = ?"
            count_params.append(status)

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return executions or [], total

    def get_execution_detail(self, execution_id: str) -> Dict:
        exec_query = """
            SELECT
                e.id,
                e.message_id,
                e.conversation_id,
                c.contact_id as customer_id,
                e.status,
                e.started_at,
                e.completed_at,
                e.total_duration,
                e.confidence,
                e.intent,
                e.sentiment,
                e.priority,
                e.escalated
            FROM executions e
            LEFT JOIN conversations c ON c.id = e.conversation_id
            WHERE e.id = ?
        """
        exec_row = self._execute_query(exec_query, (execution_id,), fetch_one=True)

        if not exec_row:
            raise NotFoundError(resource="Execution", identifier=execution_id)

        steps_query = """
            SELECT * FROM execution_steps
            WHERE execution_id = ?
            ORDER BY sequence_order
        """
        steps = self._execute_query(steps_query, (execution_id,), fetch_all=True)

        result = dict(exec_row)
        result['steps'] = steps or []
        return result

    def get_execution_timeline(self, execution_id: str) -> List[Dict]:
        exec_query = "SELECT id FROM executions WHERE id = ?"
        exec_row = self._execute_query(exec_query, (execution_id,), fetch_one=True)

        if not exec_row:
            raise NotFoundError(resource="Execution", identifier=execution_id)

        steps_query = """
            SELECT
                agent_id,
                agent_name,
                started_at,
                completed_at,
                latency as duration,
                status,
                input_data as input_summary,
                output_data as output_summary,
                error,
                sequence_order
            FROM execution_steps
            WHERE execution_id = ?
            ORDER BY sequence_order
        """
        steps = self._execute_query(steps_query, (execution_id,), fetch_all=True)
        return steps or []
