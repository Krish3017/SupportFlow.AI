from typing import Optional, List, Dict, Tuple
from repositories.base import BaseRepository
from core.errors import NotFoundError
from core.logging_config import get_logger

logger = get_logger(__name__)

AGENT_NAMES = {
    "intent": "Intent Agent",
    "customer_intelligence": "Customer Intelligence Agent",
    "priority": "Priority Agent",
    "knowledge": "Knowledge Agent",
    "resolution": "Resolution Agent",
    "escalation": "Escalation Agent",
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
            FROM agent_executions
            GROUP BY agent_id
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
            FROM agent_executions
            WHERE agent_id = ?
            GROUP BY agent_id
        """
        stats = self._execute_query(stats_query, (agent_name,), fetch_one=True)

        if not stats:
            raise NotFoundError(resource="Agent", identifier=agent_name)

        # Get recent errors
        errors_query = """
            SELECT error FROM agent_executions
            WHERE agent_id = ? AND status = 'failed' AND error IS NOT NULL
            ORDER BY started_at DESC
            LIMIT 5
        """
        errors = self._execute_query(errors_query, (agent_name,), fetch_all=True)

        # Get latency percentiles
        latency_query = """
            SELECT latency FROM agent_executions
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

        # Get distinct executions grouped by ticket_id and session
        query = """
            SELECT
                MIN(id) as id,
                ticket_id,
                session_id,
                MIN(started_at) as started_at,
                MAX(completed_at) as completed_at,
                SUM(latency) as total_duration,
                COUNT(*) as step_count,
                CASE
                    WHEN SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) > 0 THEN 'failed'
                    WHEN SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) > 0 THEN 'running'
                    ELSE 'success'
                END as status
            FROM agent_executions
            WHERE 1=1
        """
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        if ticket_id:
            query += " AND ticket_id = ?"
            params.append(ticket_id)

        query += " GROUP BY ticket_id ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        executions = self._execute_query(query, tuple(params), fetch_all=True)

        # Count
        count_query = """
            SELECT COUNT(DISTINCT ticket_id) as count
            FROM agent_executions
            WHERE 1=1
        """
        count_params = []

        if agent_id:
            count_query += " AND agent_id = ?"
            count_params.append(agent_id)

        if status:
            count_query += " AND status = ?"
            count_params.append(status)

        if ticket_id:
            count_query += " AND ticket_id = ?"
            count_params.append(ticket_id)

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return executions or [], total

    def get_execution_detail(self, execution_id: str) -> Dict:
        # First find the ticket_id for this execution
        exec_query = "SELECT ticket_id FROM agent_executions WHERE id = ?"
        exec_row = self._execute_query(exec_query, (execution_id,), fetch_one=True)

        if not exec_row:
            raise NotFoundError(resource="Execution", identifier=execution_id)

        ticket_id = exec_row['ticket_id']

        # Get all steps for this ticket's execution
        steps_query = """
            SELECT * FROM agent_executions
            WHERE ticket_id = ?
            ORDER BY sequence_order
        """
        steps = self._execute_query(steps_query, (ticket_id,), fetch_all=True)

        return {
            'id': execution_id,
            'ticket_id': ticket_id,
            'steps': steps or []
        }

    def get_execution_timeline(self, execution_id: str) -> List[Dict]:
        exec_query = "SELECT ticket_id FROM agent_executions WHERE id = ?"
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
            FROM agent_executions
            WHERE ticket_id = ?
            ORDER BY sequence_order
        """
        steps = self._execute_query(steps_query, (exec_row['ticket_id'],), fetch_all=True)
        return steps or []
