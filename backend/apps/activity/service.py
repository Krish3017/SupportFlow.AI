import json
from typing import Optional, List
from .repository import ActivityRepository
from .schemas import (
    ActivityResponse,
    ActivityListResponse,
    ActivityType,
    ActivityLevel
)
from core.logging_config import get_logger

logger = get_logger(__name__)

class ActivityService:

    def __init__(self):
        self.repository = ActivityRepository()

    def list_activities(
        self,
        activity_type: Optional[str] = None,
        level: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> ActivityListResponse:

        offset = (page - 1) * limit

        activities_data, total = self.repository.list_activities(
            activity_type=activity_type,
            level=level,
            search=search,
            limit=limit,
            offset=offset
        )

        activities = [self._to_response(a) for a in activities_data]

        return ActivityListResponse(
            activities=activities,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0
        )

    def get_activity(self, activity_id: int) -> ActivityResponse:
        data = self.repository.get_activity(activity_id)
        return self._to_response(data)

    def search_activities(self, query: str, limit: int = 20) -> List[ActivityResponse]:
        results = self.repository.search_activities(query, limit)
        return [self._to_response(r) for r in results]

    def _to_response(self, data: dict) -> ActivityResponse:
        metadata = None
        if data.get('metadata'):
            try:
                metadata = json.loads(data['metadata'])
            except (json.JSONDecodeError, TypeError):
                metadata = None

        raw_type = (data.get('type') or 'system').lower()
        try:
            act_type = ActivityType(raw_type)
        except ValueError:
            act_type = ActivityType.SYSTEM

        raw_level = (data.get('level') or 'info').lower()
        try:
            act_level = ActivityLevel(raw_level)
        except ValueError:
            act_level = ActivityLevel.INFO

        return ActivityResponse(
            id=data['id'],
            type=act_type,
            level=act_level,
            message=data['message'],
            timestamp=data['timestamp'],
            metadata=metadata
        )
