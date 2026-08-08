from typing import Optional, List, Dict, Any
from company_data.connection import get_company_db_connection


class CompanyRepository:
    """
    Data Access Repository for company business database (Supabase PostgreSQL company schema).
    Provides parameterized SQL operations and isolation from LangGraph agents.
    """

    def __init__(self, conn_factory=get_company_db_connection):
        self.conn_factory = conn_factory

    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.customers WHERE customer_id = %s", (customer_id,)
                )
                return cur.fetchone()

    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.customers WHERE LOWER(email) = LOWER(%s)", (email.strip(),)
                )
                return cur.fetchone()

    def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.customers WHERE phone = %s", (phone.strip(),)
                )
                return cur.fetchone()

    def get_addresses_by_customer_id(self, customer_id: str) -> List[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.addresses WHERE customer_id = %s ORDER BY is_default DESC", (customer_id,)
                )
                return cur.fetchall()

    def get_address_by_id(self, address_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.addresses WHERE address_id = %s", (address_id,)
                )
                return cur.fetchone()

    def get_customer_orders(self, customer_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM company.orders 
                    WHERE customer_id = %s 
                    ORDER BY order_date DESC 
                    LIMIT %s
                    """, (customer_id, limit)
                )
                return cur.fetchall()

    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.orders WHERE UPPER(order_id) = UPPER(%s)", (order_id.strip(),)
                )
                return cur.fetchone()

    def get_order_items(self, order_id: str) -> List[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT oi.*, p.product_name, p.category 
                    FROM company.order_items oi
                    JOIN company.products p ON oi.product_id = p.product_id
                    WHERE UPPER(oi.order_id) = UPPER(%s)
                    """, (order_id.strip(),)
                )
                return cur.fetchall()

    def get_payment_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.payments WHERE UPPER(order_id) = UPPER(%s) ORDER BY payment_date DESC LIMIT 1", (order_id.strip(),)
                )
                return cur.fetchone()

    def get_payment_by_id(self, payment_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.payments WHERE UPPER(payment_id) = UPPER(%s)", (payment_id.strip(),)
                )
                return cur.fetchone()

    def get_shipment_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.shipments WHERE UPPER(order_id) = UPPER(%s) ORDER BY shipped_at DESC LIMIT 1", (order_id.strip(),)
                )
                return cur.fetchone()

    def get_shipment_by_tracking(self, tracking_number: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.shipments WHERE UPPER(tracking_number) = UPPER(%s)", (tracking_number.strip(),)
                )
                return cur.fetchone()

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.products WHERE UPPER(product_id) = UPPER(%s)", (product_id.strip(),)
                )
                return cur.fetchone()

    def get_products_by_name(self, query: str) -> List[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.products WHERE LOWER(product_name) LIKE LOWER(%s) AND active_status = TRUE", (f"%{query.strip()}%",)
                )
                return cur.fetchall()

    def get_subscription_by_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM company.subscriptions WHERE customer_id = %s ORDER BY start_date DESC LIMIT 1", (customer_id,)
                )
                return cur.fetchone()
