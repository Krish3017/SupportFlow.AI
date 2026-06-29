from typing import Optional, List
from .repository import ObservatoryRepository, AGENT_NAMES
from .schemas import (
    AgentHealthResponse,
    AgentDetailResponse,
    AgentListResponse,
    AgentStatusEnum,
    ExecutionResponse,
    ExecutionDetailResponse,
    ExecutionStepResponse,
    ExecutionListResponse,
    ExecutionStatusEnum
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class ObservatoryService:

    def __init__(self):
        self.repository = ObservatoryRepository()

    def get_all_agents(self) -> AgentListResponse:
        stats_data = self.repository.get_agent_stats()
        agents_with_data = {s['agent_id']: s for s in stats_data}

        agents = []
        for agent_id, agent_name in AGENT_NAMES.items():
            if agent_id in agents_with_data:
                s = agents_with_data[agent_id]
                total = s['total_executions']
                failed = s['failed_executions']
                status = self._compute_status(total, failed)

                agents.append(AgentHealthResponse(
                    id=agent_id,
                    name=agent_name,
                    status=status,
                    total_executions=total,
                    successful_executions=s['successful_executions'],
                    failed_executions=failed,
                    avg_latency=round(s['avg_latency'] or 0, 3),
                    last_execution=s['last_execution'],
                    error_count=failed
                ))
            else:
                agents.append(AgentHealthResponse(
                    id=agent_id,
                    name=agent_name,
                    status=AgentStatusEnum.HEALTHY,
                    total_executions=0,
                    successful_executions=0,
                    failed_executions=0,
                    avg_latency=0.0,
                    last_execution=None,
                    error_count=0
                ))

        return AgentListResponse(agents=agents)

    def get_agent_detail(self, agent_name: str) -> AgentDetailResponse:
        data = self.repository.get_agent_detail(agent_name)

        total = data['total_executions']
        failed = data['failed_executions']
        successful = data['successful_executions']
        status = self._compute_status(total, failed)

        latencies = data.get('latencies', [])
        p50 = self._percentile(latencies, 50)
        p95 = self._percentile(latencies, 95)
        p99 = self._percentile(latencies, 99)

        success_rate = (successful / total * 100) if total > 0 else 0.0

        return AgentDetailResponse(
            id=data['agent_id'],
            name=data['agent_name'],
            status=status,
            total_executions=total,
            successful_executions=successful,
            failed_executions=failed,
            avg_latency=round(data['avg_latency'] or 0, 3),
            last_execution=data['last_execution'],
            error_count=failed,
            recent_errors=data.get('recent_errors', []),
            latency_p50=round(p50, 3),
            latency_p95=round(p95, 3),
            latency_p99=round(p99, 3),
            success_rate=round(success_rate, 1)
        )

    def list_executions(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        ticket_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> ExecutionListResponse:

        offset = (page - 1) * limit

        executions_data, total = self.repository.list_executions(
            agent_id=agent_id,
            status=status,
            ticket_id=ticket_id,
            search=search,
            limit=limit,
            offset=offset
        )

        executions = [
            ExecutionResponse(
                id=e['id'],
                conversation_id=e['conversation_id'],
                message_id=e.get('message_id'),
                started_at=e['started_at'],
                completed_at=e.get('completed_at'),
                total_duration=round(e.get('total_duration') or 0, 3),
                status=self._safe_status(e['status']),
                step_count=e.get('step_count', 0),
                intent=e.get('intent'),
                confidence=e.get('confidence'),
                escalated=bool(e.get('escalated', 0))
            )
            for e in executions_data
        ]

        return ExecutionListResponse(
            executions=executions,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0
        )

    def get_execution_detail(self, execution_id: str) -> ExecutionDetailResponse:
        data = self.repository.get_execution_detail(execution_id)
        steps_data = data['steps']

        steps = [
            ExecutionStepResponse(
                agent_name=s['agent_name'],
                started_at=s['started_at'],
                completed_at=s.get('completed_at'),
                duration=round(s.get('latency') or 0, 3),
                status=self._safe_status(s['status']),
                input_summary=self._safe_summary(s.get('input_data')),
                output_summary=self._safe_summary(s.get('output_data')),
                error=s.get('error'),
                sequence_order=s.get('sequence_order', 0)
            )
            for s in steps_data
        ]

        total_duration = sum(s.duration for s in steps)
        overall_status = self._safe_status(data.get('status', 'completed'))

        return ExecutionDetailResponse(
            id=data['id'],
            conversation_id=data['conversation_id'],
            message_id=data.get('message_id'),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            total_duration=round(total_duration, 3),
            status=overall_status,
            step_count=len(steps),
            intent=data.get('intent'),
            confidence=data.get('confidence'),
            steps=steps
        )

    def get_execution_timeline(self, execution_id: str) -> List[ExecutionStepResponse]:
        steps_data = self.repository.get_execution_timeline(execution_id)

        return [
            ExecutionStepResponse(
                agent_name=s['agent_name'],
                started_at=s['started_at'],
                completed_at=s.get('completed_at'),
                duration=round(s.get('duration') or 0, 3),
                status=self._safe_status(s['status']),
                input_summary=self._safe_summary(s.get('input_summary')),
                output_summary=self._safe_summary(s.get('output_summary')),
                error=s.get('error'),
                sequence_order=s.get('sequence_order', 0)
            )
            for s in steps_data
        ]

    def _compute_status(self, total: int, failed: int) -> AgentStatusEnum:
        if total == 0:
            return AgentStatusEnum.HEALTHY
        failure_rate = failed / total
        if failure_rate > 0.3:
            return AgentStatusEnum.OFFLINE
        elif failure_rate > 0.1:
            return AgentStatusEnum.DEGRADED
        return AgentStatusEnum.HEALTHY

    def _percentile(self, values: List[float], pct: int) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        idx = int(len(sorted_values) * pct / 100)
        idx = min(idx, len(sorted_values) - 1)
        return sorted_values[idx]

    def _safe_summary(self, data: Optional[str]) -> Optional[str]:
        if not data:
            return None
        if len(data) > 200:
            return data[:200] + "..."
        return data

    def _safe_status(self, status: str) -> ExecutionStatusEnum:
        try:
            return ExecutionStatusEnum(status)
        except ValueError:
            return ExecutionStatusEnum.COMPLETED
