import json
from typing import Optional, List, Dict, Tuple
from repositories.base import BaseRepository
from core.errors import NotFoundError
from core.logging_config import get_logger

logger = get_logger(__name__)

class ActivityRepository(BaseRepository):

    def list_activities(
        self,
        activity_type: Optional[str] = None,
        level: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:

        query = "SELECT * FROM activity_logs WHERE 1=1"
        params = []

        if activity_type:
            query += " AND type = ?"
            params.append(activity_type)

        if level:
            query += " AND level = ?"
            params.append(level)

        if search:
            query += " AND message LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        activities = self._execute_query(query, tuple(params), fetch_all=True)

        count_query = "SELECT COUNT(*) as count FROM activity_logs WHERE 1=1"
        count_params = []

        if activity_type:
            count_query += " AND type = ?"
            count_params.append(activity_type)
        if level:
            count_query += " AND level = ?"
            count_params.append(level)
        if search:
            count_query += " AND message LIKE ?"
            count_params.append(f"%{search}%")

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return activities or [], total

    def get_activity(self, activity_id: int) -> Dict:
        query = "SELECT * FROM activity_logs WHERE id = ?"
        result = self._execute_query(query, (activity_id,), fetch_one=True)

        if not result:
            raise NotFoundError(resource="Activity", identifier=str(activity_id))

        return result

    def search_activities(self, query: str, limit: int = 20) -> List[Dict]:
        search_query = """
            SELECT * FROM activity_logs
            WHERE message LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        results = self._execute_query(search_query, (f"%{query}%", limit), fetch_all=True)
        return results or []
