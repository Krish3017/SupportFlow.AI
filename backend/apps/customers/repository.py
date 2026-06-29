from typing import Optional, List, Dict, Tuple
from repositories.base import BaseRepository
from core.errors import NotFoundError
from utils.filtering import QueryBuilder, SortOrder
from core.logging_config import get_logger

logger = get_logger(__name__)

class CustomerRepository(BaseRepository):

    def list_customers(
        self,
        tier: Optional[str] = None,
        sentiment: Optional[str] = None,
        min_risk_score: Optional[int] = None,
        max_risk_score: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:

        query = "SELECT * FROM customers WHERE 1=1"
        params = []

        if tier:
            query += " AND tier = ?"
            params.append(tier)

        if sentiment:
            query += " AND sentiment = ?"
            params.append(sentiment)

        if min_risk_score is not None:
            query += " AND risk_score >= ?"
            params.append(min_risk_score)

        if max_risk_score is not None:
            query += " AND risk_score <= ?"
            params.append(max_risk_score)

        if search:
            query += " AND (email LIKE ? OR name LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])

        query += " ORDER BY COALESCE(last_interaction, joined_date) DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        customers = self._execute_query(query, tuple(params), fetch_all=True)

        # Count
        count_query = "SELECT COUNT(*) as count FROM customers WHERE 1=1"
        count_params = []

        if tier:
            count_query += " AND tier = ?"
            count_params.append(tier)

        if sentiment:
            count_query += " AND sentiment = ?"
            count_params.append(sentiment)

        if min_risk_score is not None:
            count_query += " AND risk_score >= ?"
            count_params.append(min_risk_score)

        if max_risk_score is not None:
            count_query += " AND risk_score <= ?"
            count_params.append(max_risk_score)

        if search:
            count_query += " AND (email LIKE ? OR name LIKE ?)"
            search_param = f"%{search}%"
            count_params.extend([search_param, search_param])

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return customers, total

    def get_customer(self, customer_id: str) -> Optional[Dict]:
        query = "SELECT * FROM customers WHERE id = ?"
        customer = self._execute_query(query, (customer_id,), fetch_one=True)

        if not customer:
            raise NotFoundError(resource="Customer", identifier=customer_id)

        return customer

    def get_customer_tickets(self, customer_id: str) -> List[Dict]:
        query = """
            SELECT id, subject, status, priority, created_at
            FROM tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC
        """
        tickets = self._execute_query(query, (customer_id,), fetch_all=True)
        return tickets or []

    def get_customer_conversations(self, customer_id: str) -> List[Dict]:
        query = """
            SELECT
                c.id,
                t.channel,
                c.timestamp as started_at
            FROM conversations c
            LEFT JOIN tickets t ON CAST(c.id AS TEXT) = t.id
            WHERE t.customer_id = ?
            ORDER BY c.timestamp DESC
        """
        conversations = self._execute_query(query, (customer_id,), fetch_all=True)
        return conversations or []

    def search_customers(self, query: str, limit: int = 20) -> List[Dict]:
        search_query = """
            SELECT * FROM customers
            WHERE email LIKE ? OR name LIKE ?
            ORDER BY last_interaction DESC
            LIMIT ?
        """
        search_param = f"%{query}%"
        results = self._execute_query(
            search_query,
            (search_param, search_param, limit),
            fetch_all=True
        )
        return results or []

    def get_customer_stats(self, customer_id: str) -> Dict:
        stats_query = """
            SELECT
                COUNT(*) as total_tickets,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_tickets,
                SUM(CASE WHEN status = 'escalated' THEN 1 ELSE 0 END) as escalated_tickets,
                SUM(CASE WHEN status IN ('new', 'in_progress') THEN 1 ELSE 0 END) as open_tickets
            FROM tickets
            WHERE customer_id = ?
        """
        stats = self._execute_query(stats_query, (customer_id,), fetch_one=True)
        return dict(stats) if stats else {
            'total_tickets': 0,
            'resolved_tickets': 0,
            'escalated_tickets': 0,
            'open_tickets': 0
        }
