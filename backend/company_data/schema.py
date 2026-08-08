import sqlite3
import logging

logger = logging.getLogger(__name__)

CREATE_CUSTOMERS_TABLE = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    customer_tier TEXT DEFAULT 'Bronze',
    account_status TEXT DEFAULT 'active',
    registration_date TEXT NOT NULL,
    total_orders INTEGER DEFAULT 0,
    total_spent REAL DEFAULT 0.0,
    preferred_channel TEXT DEFAULT 'email',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

CREATE_ADDRESSES_TABLE = """
CREATE TABLE IF NOT EXISTS addresses (
    address_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    address_type TEXT DEFAULT 'shipping',
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL,
    is_default INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
"""

CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock_status TEXT DEFAULT 'in_stock',
    active_status INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

CREATE_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    total_amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    shipping_address_id TEXT,
    expected_delivery_date TEXT,
    actual_delivery_date TEXT,
    tracking_information TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id) ON DELETE SET NULL
);
"""

CREATE_ORDER_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS order_items (
    item_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);
"""

CREATE_PAYMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    transaction_reference TEXT,
    payment_date TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
"""

CREATE_SHIPMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    carrier TEXT NOT NULL,
    tracking_number TEXT NOT NULL,
    shipment_status TEXT NOT NULL,
    shipped_at TEXT,
    estimated_delivery TEXT,
    delivered_at TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);
"""

CREATE_SUBSCRIPTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    plan TEXT NOT NULL,
    status TEXT NOT NULL,
    billing_cycle TEXT NOT NULL,
    start_date TEXT NOT NULL,
    renewal_date TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
"""


def create_company_schema(conn: sqlite3.Connection) -> None:
    """
    Creates all tables for the company business database.
    """
    cursor = conn.cursor()
    cursor.execute(CREATE_CUSTOMERS_TABLE)
    cursor.execute(CREATE_ADDRESSES_TABLE)
    cursor.execute(CREATE_PRODUCTS_TABLE)
    cursor.execute(CREATE_ORDERS_TABLE)
    cursor.execute(CREATE_ORDER_ITEMS_TABLE)
    cursor.execute(CREATE_PAYMENTS_TABLE)
    cursor.execute(CREATE_SHIPMENTS_TABLE)
    cursor.execute(CREATE_SUBSCRIPTIONS_TABLE)
    conn.commit()
    logger.info("Company business database schema initialized.")
