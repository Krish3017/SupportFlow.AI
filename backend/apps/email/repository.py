from typing import Optional, List, Dict, Tuple
from repositories.base import BaseRepository
from core.errors import NotFoundError
from core.logging_config import get_logger

logger = get_logger(__name__)

class EmailRepository(BaseRepository):

    def list_emails(
        self,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:

        query = "SELECT * FROM email_tickets WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if search:
            query += " AND (subject LIKE ? OR sender_email LIKE ? OR body LIKE ?)"
            s = f"%{search}%"
            params.extend([s, s, s])

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        emails = self._execute_query(query, tuple(params), fetch_all=True)

        count_query = "SELECT COUNT(*) as count FROM email_tickets WHERE 1=1"
        count_params = []

        if status:
            count_query += " AND status = ?"
            count_params.append(status)
        if search:
            count_query += " AND (subject LIKE ? OR sender_email LIKE ? OR body LIKE ?)"
            s = f"%{search}%"
            count_params.extend([s, s, s])

        count_result = self._execute_query(count_query, tuple(count_params), fetch_one=True)
        total = count_result['count'] if count_result else 0

        return emails or [], total

    def get_email(self, email_id: int) -> Dict:
        query = "SELECT * FROM email_tickets WHERE id = ?"
        result = self._execute_query(query, (email_id,), fetch_one=True)

        if not result:
            raise NotFoundError(resource="Email", identifier=str(email_id))

        return result

    def get_linked_ticket(self, conversation_id: str) -> Optional[Dict]:
        """
        Look up a ticket that is linked to the given conversation.
        Returns None if no ticket exists (most conversations are not escalated).
        """
        if not conversation_id:
            return None
        query = """
            SELECT id, subject, status, priority, created_at
            FROM tickets
            WHERE conversation_id = ?
            LIMIT 1
        """
        return self._execute_query(query, (conversation_id,), fetch_one=True)

    def update_status(self, email_id: int, status: str, ai_response: Optional[str] = None) -> None:
        if ai_response:
            query = "UPDATE email_tickets SET status = %s, ai_response = %s WHERE id = %s"
            self._execute_query(query, (status, ai_response, email_id))
        else:
            query = "UPDATE email_tickets SET status = %s WHERE id = %s"
            self._execute_query(query, (status, email_id))

    def is_email_processed(self, gmail_message_id: str) -> bool:
        query = "SELECT id FROM email_tickets WHERE gmail_message_id = %s"
        result = self._execute_query(query, (gmail_message_id,), fetch_one=True)
        return result is not None

    def save_email_ticket(self, email: dict) -> int:
        from datetime import datetime
        query = """
            INSERT INTO email_tickets (gmail_message_id, sender_email, subject, body, status, created_at)
            VALUES (%s, %s, %s, %s, 'pending', %s)
            ON CONFLICT (gmail_message_id) DO NOTHING
            RETURNING id
        """
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    email["id"],
                    email["sender"],
                    email["subject"],
                    email["body"],
                    now
                ))
                row = cur.fetchone()
                if row:
                    return row['id']
                
                cur.execute("SELECT id FROM email_tickets WHERE gmail_message_id = %s", (email["id"],))
                existing = cur.fetchone()
                return existing['id'] if existing else 0

    def link_conversation(self, email_id: int, conversation_id: str) -> None:
        query = "UPDATE email_tickets SET conversation_id = %s WHERE id = %s"
        self._execute_query(query, (conversation_id, email_id))

    def search_emails(self, query: str, limit: int = 20) -> List[Dict]:
        search_query = """
            SELECT * FROM email_tickets
            WHERE subject ILIKE %s OR sender_email ILIKE %s OR body ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        s = f"%{query}%"
        results = self._execute_query(search_query, (s, s, s, limit), fetch_all=True)
        return results or []
