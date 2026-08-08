import sqlite3
from typing import Optional, List, Dict, Any
from company_data.connection import get_company_db_connection


class CompanyRepository:
    """
    Data Access Repository for company business database.
    Provides parameterized SQL operations and isolation from LangGraph agents.
    """

    def __init__(self, conn_factory=get_company_db_connection):
        self.conn_factory = conn_factory

    def _dict_row(self, row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
        return dict(row) if row else None

    def _dict_rows(self, rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        return [dict(r) for r in rows]

    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE customer_id = ?", (customer_id,)
            ).fetchone()
            return self._dict_row(row)

    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE LOWER(email) = LOWER(?)", (email.strip(),)
            ).fetchone()
            return self._dict_row(row)

    def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE phone = ?", (phone.strip(),)
            ).fetchone()
            return self._dict_row(row)

    def get_addresses_by_customer_id(self, customer_id: str) -> List[Dict[str, Any]]:
        with self.conn_factory() as conn:
            rows = conn.execute(
                "SELECT * FROM addresses WHERE customer_id = ? ORDER BY is_default DESC", (customer_id,)
            ).fetchall()
            return self._dict_rows(rows)

    def get_address_by_id(self, address_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM addresses WHERE address_id = ?", (address_id,)
            ).fetchone()
            return self._dict_row(row)

    def get_customer_orders(self, customer_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        with self.conn_factory() as conn:
            rows = conn.execute(
                """
                SELECT * FROM orders 
                WHERE customer_id = ? 
                ORDER BY order_date DESC 
                LIMIT ?
                """, (customer_id, limit)
            ).fetchall()
            return self._dict_rows(rows)

    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM orders WHERE UPPER(order_id) = UPPER(?)", (order_id.strip(),)
            ).fetchone()
            return self._dict_row(row)

    def get_order_items(self, order_id: str) -> List[Dict[str, Any]]:
        with self.conn_factory() as conn:
            rows = conn.execute(
                """
                SELECT oi.*, p.product_name, p.category 
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE UPPER(oi.order_id) = UPPER(?)
                """, (order_id.strip(),)
            ).fetchall()
            return self._dict_rows(rows)

    def get_payment_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM payments WHERE UPPER(order_id) = UPPER(?) ORDER BY payment_date DESC LIMIT 1", (order_id.strip(),)
            ).fetchone()
            return self._dict_row(row)

    def get_payment_by_id(self, payment_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM payments WHERE UPPER(payment_id) = UPPER(?)", (payment_id.strip(),)
            ).fetchone()
            return self._dict_row(row)

    def get_shipment_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM shipments WHERE UPPER(order_id) = UPPER(?) ORDER BY shipped_at DESC LIMIT 1", (order_id.strip(),)
            ).fetchone()
            return self._dict_row(row)

    def get_shipment_by_tracking(self, tracking_number: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM shipments WHERE UPPER(tracking_number) = UPPER(?)", (tracking_number.strip(),)
            ).fetchone()
            return self._dict_row(row)

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE UPPER(product_id) = UPPER(?)", (product_id.strip(),)
            ).fetchone()
            return self._dict_row(row)

    def get_products_by_name(self, query: str) -> List[Dict[str, Any]]:
        with self.conn_factory() as conn:
            rows = conn.execute(
                "SELECT * FROM products WHERE LOWER(product_name) LIKE LOWER(?) AND active_status = 1", (f"%{query.strip()}%",)
            ).fetchall()
            return self._dict_rows(rows)

    def get_subscription_by_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            row = conn.execute(
                "SELECT * FROM subscriptions WHERE customer_id = ? ORDER BY start_date DESC LIMIT 1", (customer_id,)
            ).fetchone()
            return self._dict_row(row)
