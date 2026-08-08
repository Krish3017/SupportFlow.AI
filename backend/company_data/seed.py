import logging
from company_data.connection import get_company_db_connection
from company_data.schema import create_company_schema

logger = logging.getLogger(__name__)


def seed_company_database() -> None:
    """
    Deterministically seeds 22 realistic synthetic customers and related business data.
    Uses INSERT OR REPLACE to ensure idempotency.
    """
    conn = get_company_db_connection()
    try:
        create_company_schema(conn)
        cursor = conn.cursor()

        now = "2026-08-08T10:00:00Z"

        # 1. Synthetic Products (12 items)
        products = [
            ("PROD-101", "Wireless Noise-Canceling Headphones", "Premium over-ear wireless headphones with active noise cancellation.", "Electronics", 249.99, "in_stock", 1, now, now),
            ("PROD-102", "Smart Fitness Watch", "Fitness tracker with heart rate monitor, GPS, and sleep analysis.", "Electronics", 129.99, "in_stock", 1, now, now),
            ("PROD-103", "Mechanical Gaming Keyboard", "RGB mechanical keyboard with tactile blue switches.", "Electronics", 89.99, "in_stock", 1, now, now),
            ("PROD-104", "Ultra-Wide 4K Monitor 34-inch", "34-inch curved IPS panel 144Hz monitor for productivity and gaming.", "Electronics", 599.99, "in_stock", 1, now, now),
            ("PROD-105", "Ergonomic Mesh Executive Chair", "High-back ergonomic desk chair with lumbar support and adjustable armrests.", "Furniture", 299.99, "in_stock", 1, now, now),
            ("PROD-106", "USB-C 10-in-1 Hub", "Multiport USB-C adapter with HDMI, Ethernet, and SD card reader.", "Accessories", 49.99, "in_stock", 1, now, now),
            ("PROD-107", "Portable SSD 1TB", "High-speed USB 3.2 Gen 2 portable solid state drive.", "Storage", 109.99, "in_stock", 1, now, now),
            ("PROD-108", "HD 1080p Streaming Webcam", "Full HD webcam with dual microphones and privacy shutter.", "Electronics", 69.99, "out_of_stock", 1, now, now),
            ("PROD-109", "Bluetooth Waterproof Speaker", "Rugged outdoor portable speaker with 20-hour battery life.", "Audio", 79.99, "in_stock", 1, now, now),
            ("PROD-110", "Fast Wireless Charging Stand", "15W Qi-certified fast wireless charger for smartphones.", "Accessories", 29.99, "in_stock", 1, now, now),
            ("PROD-111", "Ergonomic Wireless Vertical Mouse", "Optical vertical mouse to reduce wrist strain.", "Accessories", 39.99, "in_stock", 1, now, now),
            ("PROD-112", "Aluminum Adjustable Laptop Stand", "Foldable ventilation laptop riser compatible with 10-17 inch laptops.", "Accessories", 34.99, "in_stock", 1, now, now),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO products
            (product_id, product_name, description, category, price, stock_status, active_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products)

        # 2. Synthetic Customers (22 customers)
        customers = [
            ("CUST-1001", "Alice Johnson", "alice.johnson@example.com", "+1-555-0101", "Gold", "active", "2024-01-15T09:00:00Z", 3, 479.97, "email", "2024-01-15T09:00:00Z", now),
            ("CUST-1002", "Bob Smith", "bob.smith@example.com", "+1-555-0102", "Silver", "active", "2024-02-10T10:30:00Z", 2, 219.98, "chat", "2024-02-10T10:30:00Z", now),
            ("CUST-1003", "Carol Williams", "carol.williams@example.com", "+1-555-0103", "Platinum", "active", "2023-11-05T14:20:00Z", 4, 1149.96, "telegram", "2023-11-05T14:20:00Z", now),
            ("CUST-1004", "David Brown", "david.brown@example.com", "+1-555-0104", "Bronze", "active", "2024-03-01T11:00:00Z", 1, 89.99, "email", "2024-03-01T11:00:00Z", now),
            ("CUST-1005", "Emily Davis", "emily.davis@example.com", "+1-555-0105", "VIP", "active", "2023-08-19T16:45:00Z", 5, 1499.95, "email", "2023-08-19T16:45:00Z", now),
            ("CUST-1006", "Frank Wilson", "frank.wilson@example.com", "+1-555-0106", "Bronze", "suspended", "2024-04-12T08:15:00Z", 1, 49.99, "chat", "2024-04-12T08:15:00Z", now),
            ("CUST-1007", "Grace Taylor", "grace.taylor@example.com", "+1-555-0107", "Silver", "active", "2024-01-22T13:10:00Z", 2, 339.98, "email", "2024-01-22T13:10:00Z", now),
            ("CUST-1008", "Henry Anderson", "henry.anderson@example.com", "+1-555-0108", "Gold", "active", "2023-12-01T09:30:00Z", 3, 729.97, "chat", "2023-12-01T09:30:00Z", now),
            ("CUST-1009", "Isabella Thomas", "isabella.thomas@example.com", "+1-555-0109", "Bronze", "active", "2024-05-05T12:00:00Z", 1, 129.99, "email", "2024-05-05T12:00:00Z", now),
            ("CUST-1010", "Jack Jackson", "jack.jackson@example.com", "+1-555-0110", "Silver", "active", "2024-02-28T15:20:00Z", 2, 179.98, "telegram", "2024-02-28T15:20:00Z", now),
            ("CUST-1011", "Karen White", "karen.white@example.com", "+1-555-0111", "Gold", "active", "2023-10-14T11:40:00Z", 3, 549.97, "email", "2023-10-14T11:40:00Z", now),
            ("CUST-1012", "Liam Harris", "liam.harris@example.com", "+1-555-0112", "Bronze", "active", "2024-06-01T10:00:00Z", 1, 69.99, "chat", "2024-06-01T10:00:00Z", now),
            ("CUST-1013", "Mia Martin", "mia.martin@example.com", "+1-555-0113", "Platinum", "active", "2023-09-09T08:50:00Z", 4, 989.96, "email", "2023-09-09T08:50:00Z", now),
            ("CUST-1014", "Noah Thompson", "noah.thompson@example.com", "+1-555-0114", "Bronze", "inactive", "2024-03-15T14:00:00Z", 0, 0.0, "email", "2024-03-15T14:00:00Z", now),
            ("CUST-1015", "Olivia Garcia", "olivia.garcia@example.com", "+1-555-0115", "Silver", "active", "2024-01-08T17:30:00Z", 2, 359.98, "email", "2024-01-08T17:30:00Z", now),
            ("CUST-1016", "Peter Martinez", "peter.martinez@example.com", "+1-555-0116", "Gold", "active", "2023-11-20T10:15:00Z", 3, 629.97, "telegram", "2023-11-20T10:15:00Z", now),
            ("CUST-1017", "Quinn Robinson", "quinn.robinson@example.com", "+1-555-0117", "Bronze", "active", "2024-04-02T13:45:00Z", 1, 39.99, "chat", "2024-04-02T13:45:00Z", now),
            ("CUST-1018", "Rachel Clark", "rachel.clark@example.com", "+1-555-0118", "VIP", "active", "2023-07-04T09:00:00Z", 6, 2199.94, "email", "2023-07-04T09:00:00Z", now),
            ("CUST-1019", "Samuel Rodriguez", "samuel.rodriguez@example.com", "+1-555-0119", "Silver", "active", "2024-02-18T16:10:00Z", 2, 259.98, "chat", "2024-02-18T16:10:00Z", now),
            ("CUST-1020", "Tina Lewis", "tina.lewis@example.com", "+1-555-0120", "Gold", "active", "2023-12-15T11:25:00Z", 3, 499.97, "email", "2023-12-15T11:25:00Z", now),
            ("CUST-1021", "Victor Lee", "victor.lee@example.com", "+1-555-0121", "Bronze", "active", "2024-05-20T14:30:00Z", 1, 79.99, "telegram", "2024-05-20T14:30:00Z", now),
            ("CUST-1022", "Wendy Walker", "wendy.walker@example.com", "+1-555-0122", "Silver", "active", "2024-01-30T10:00:00Z", 2, 389.98, "email", "2024-01-30T10:00:00Z", now),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO customers
            (customer_id, name, email, phone, customer_tier, account_status, registration_date, total_orders, total_spent, preferred_channel, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customers)

        # 3. Synthetic Addresses
        addresses = [
            ("ADDR-1001", "CUST-1001", "shipping", "123 Market Street, Apt 4B", "San Francisco", "CA", "94105", "USA", 1, "2024-01-15T09:00:00Z", now),
            ("ADDR-1002", "CUST-1002", "shipping", "456 Oak Avenue", "Seattle", "WA", "98101", "USA", 1, "2024-02-10T10:30:00Z", now),
            ("ADDR-1003", "CUST-1003", "shipping", "789 Pine Road", "Austin", "TX", "78701", "USA", 1, "2023-11-05T14:20:00Z", now),
            ("ADDR-1004", "CUST-1004", "shipping", "101 Maple Drive", "Chicago", "IL", "60601", "USA", 1, "2024-03-01T11:00:00Z", now),
            ("ADDR-1005", "CUST-1005", "shipping", "202 Birch Boulevard", "New York", "NY", "10001", "USA", 1, "2023-08-19T16:45:00Z", now),
            ("ADDR-1006", "CUST-1006", "shipping", "303 Cedar Lane", "Denver", "CO", "80202", "USA", 1, "2024-04-12T08:15:00Z", now),
            ("ADDR-1007", "CUST-1007", "shipping", "404 Elm Court", "Boston", "MA", "02108", "USA", 1, "2024-01-22T13:10:00Z", now),
            ("ADDR-1008", "CUST-1008", "shipping", "505 Spruce Way", "Atlanta", "GA", "30303", "USA", 1, "2023-12-01T09:30:00Z", now),
            ("ADDR-1009", "CUST-1009", "shipping", "606 Willow Circle", "Miami", "FL", "33101", "USA", 1, "2024-05-05T12:00:00Z", now),
            ("ADDR-1010", "CUST-1010", "shipping", "707 Ash Pass", "Phoenix", "AZ", "85001", "USA", 1, "2024-02-28T15:20:00Z", now),
            ("ADDR-1011", "CUST-1011", "shipping", "808 Beech Street", "Portland", "OR", "97201", "USA", 1, "2023-10-14T11:40:00Z", now),
            ("ADDR-1012", "CUST-1012", "shipping", "909 Cypress Terrace", "San Diego", "CA", "92101", "USA", 1, "2024-06-01T10:00:00Z", now),
            ("ADDR-1013", "CUST-1013", "shipping", "111 Magnolia Lane", "Dallas", "TX", "75201", "USA", 1, "2023-09-09T08:50:00Z", now),
            ("ADDR-1014", "CUST-1014", "shipping", "112 Magnolia Lane", "Dallas", "TX", "75201", "USA", 1, "2024-03-15T14:00:00Z", now),
            ("ADDR-1015", "CUST-1015", "shipping", "222 Poplar Street", "Las Vegas", "NV", "89101", "USA", 1, "2024-01-08T17:30:00Z", now),
            ("ADDR-1016", "CUST-1016", "shipping", "333 Redwood Highway", "San Jose", "CA", "95101", "USA", 1, "2023-11-20T10:15:00Z", now),
            ("ADDR-1017", "CUST-1017", "shipping", "334 Redwood Highway", "San Jose", "CA", "95101", "USA", 1, "2024-04-02T13:45:00Z", now),
            ("ADDR-1018", "CUST-1018", "shipping", "444 Sycamore Drive", "Minneapolis", "MN", "55401", "USA", 1, "2023-07-04T09:00:00Z", now),
            ("ADDR-1019", "CUST-1019", "shipping", "445 Sycamore Drive", "Minneapolis", "MN", "55401", "USA", 1, "2024-02-18T16:10:00Z", now),
            ("ADDR-1020", "CUST-1020", "shipping", "555 Walnut Place", "Charlotte", "NC", "28202", "USA", 1, "2023-12-15T11:25:00Z", now),
            ("ADDR-1021", "CUST-1021", "shipping", "556 Walnut Place", "Charlotte", "NC", "28202", "USA", 1, "2024-05-20T14:30:00Z", now),
            ("ADDR-1022", "CUST-1022", "shipping", "557 Walnut Place", "Charlotte", "NC", "28202", "USA", 1, "2024-01-30T10:00:00Z", now),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO addresses
            (address_id, customer_id, address_type, street, city, state, postal_code, country, is_default, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, addresses)

        # 4. Synthetic Orders (20 orders)
        orders = [
            ("ORD-1001", "CUST-1001", "2026-08-05T10:00:00Z", "shipped", 249.99, "USD", "ADDR-1001", "2026-08-10", None, "FX10012398", "2026-08-05T10:00:00Z", now),
            ("ORD-1002", "CUST-1001", "2026-07-15T14:30:00Z", "delivered", 129.99, "USD", "ADDR-1001", "2026-07-20", "2026-07-19", "UPS9876543", "2026-07-15T14:30:00Z", now),
            ("ORD-1003", "CUST-1001", "2026-06-01T09:15:00Z", "delivered", 99.99, "USD", "ADDR-1001", "2026-06-05", "2026-06-05", "USPS456123", "2026-06-01T09:15:00Z", now),
            ("ORD-1004", "CUST-1002", "2026-08-02T11:20:00Z", "processing", 129.99, "USD", "ADDR-1002", "2026-08-12", None, "DHL4561237", "2026-08-02T11:20:00Z", now),
            ("ORD-1005", "CUST-1003", "2026-08-01T15:00:00Z", "delivered", 599.99, "USD", "ADDR-1003", "2026-08-06", "2026-08-05", "FX99887766", "2026-08-01T15:00:00Z", now),
            ("ORD-1006", "CUST-1003", "2026-07-10T12:00:00Z", "returned", 249.99, "USD", "ADDR-1003", "2026-07-15", "2026-07-14", "UPS123987", "2026-07-10T12:00:00Z", now),
            ("ORD-1007", "CUST-1004", "2026-07-25T16:30:00Z", "delivered", 89.99, "USD", "ADDR-1004", "2026-07-30", "2026-07-29", "USPS776655", "2026-07-25T16:30:00Z", now),
            ("ORD-1008", "CUST-1005", "2026-08-06T09:45:00Z", "pending", 299.99, "USD", "ADDR-1005", "2026-08-14", None, "TBD", "2026-08-06T09:45:00Z", now),
            ("ORD-1009", "CUST-1005", "2026-07-01T10:00:00Z", "delivered", 599.99, "USD", "ADDR-1005", "2026-07-06", "2026-07-06", "FX33445566", "2026-07-01T10:00:00Z", now),
            ("ORD-1010", "CUST-1005", "2026-05-15T14:00:00Z", "cancelled", 599.97, "USD", "ADDR-1005", None, None, None, "2026-05-15T14:00:00Z", now),
            ("ORD-1011", "CUST-1007", "2026-08-04T11:00:00Z", "shipped", 299.99, "USD", "ADDR-1007", "2026-08-09", None, "UPS55667788", "2026-08-04T11:00:00Z", now),
            ("ORD-1012", "CUST-1008", "2026-08-03T13:15:00Z", "delivered", 249.99, "USD", "ADDR-1008", "2026-08-07", "2026-08-07", "DHL99881122", "2026-08-03T13:15:00Z", now),
            ("ORD-1013", "CUST-1009", "2026-07-28T10:30:00Z", "delivered", 129.99, "USD", "ADDR-1009", "2026-08-02", "2026-08-01", "USPS332211", "2026-07-28T10:30:00Z", now),
            ("ORD-1014", "CUST-1010", "2026-08-07T08:00:00Z", "confirmed", 179.98, "USD", "ADDR-1010", "2026-08-15", None, "TBD", "2026-08-07T08:00:00Z", now),
            ("ORD-1015", "CUST-1011", "2026-08-02T15:45:00Z", "shipped", 249.99, "USD", "ADDR-1011", "2026-08-08", None, "FX44332211", "2026-08-02T15:45:00Z", now),
            ("ORD-1016", "CUST-1013", "2026-08-05T12:30:00Z", "processing", 599.99, "USD", "ADDR-1013", "2026-08-11", None, "TBD", "2026-08-05T12:30:00Z", now),
            ("ORD-1017", "CUST-1015", "2026-07-20T09:00:00Z", "delivered", 299.99, "USD", "ADDR-1015", "2026-07-25", "2026-07-24", "UPS88776655", "2026-07-20T09:00:00Z", now),
            ("ORD-1018", "CUST-1016", "2026-08-01T14:10:00Z", "shipped", 109.99, "USD", "ADDR-1016", "2026-08-07", None, "DHL66554433", "2026-08-01T14:10:00Z", now),
            ("ORD-1019", "CUST-1018", "2026-08-06T16:00:00Z", "processing", 599.99, "USD", "ADDR-1018", "2026-08-13", None, "TBD", "2026-08-06T16:00:00Z", now),
            ("ORD-1020", "CUST-1020", "2026-07-30T10:00:00Z", "delivered", 249.99, "USD", "ADDR-1020", "2026-08-04", "2026-08-04", "USPS990011", "2026-07-30T10:00:00Z", now),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO orders
            (order_id, customer_id, order_date, status, total_amount, currency, shipping_address_id, expected_delivery_date, actual_delivery_date, tracking_information, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, orders)

        # 5. Synthetic Order Items
        order_items = [
            ("ITEM-1001", "ORD-1001", "PROD-101", 1, 249.99, 249.99),
            ("ITEM-1002", "ORD-1002", "PROD-102", 1, 129.99, 129.99),
            ("ITEM-1003", "ORD-1003", "PROD-103", 1, 89.99, 89.99),
            ("ITEM-1004", "ORD-1004", "PROD-102", 1, 129.99, 129.99),
            ("ITEM-1005", "ORD-1005", "PROD-104", 1, 599.99, 599.99),
            ("ITEM-1006", "ORD-1006", "PROD-101", 1, 249.99, 249.99),
            ("ITEM-1007", "ORD-1007", "PROD-103", 1, 89.99, 89.99),
            ("ITEM-1008", "ORD-1008", "PROD-105", 1, 299.99, 299.99),
            ("ITEM-1009", "ORD-1009", "PROD-104", 1, 599.99, 599.99),
            ("ITEM-1010", "ORD-1011", "PROD-105", 1, 299.99, 299.99),
            ("ITEM-1011", "ORD-1012", "PROD-101", 1, 249.99, 249.99),
            ("ITEM-1012", "ORD-1015", "PROD-101", 1, 249.99, 249.99),
            ("ITEM-1013", "ORD-1016", "PROD-104", 1, 599.99, 599.99),
            ("ITEM-1014", "ORD-1018", "PROD-107", 1, 109.99, 109.99),
            ("ITEM-1015", "ORD-1020", "PROD-101", 1, 249.99, 249.99),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO order_items
            (item_id, order_id, product_id, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, order_items)

        # 6. Synthetic Payments
        payments = [
            ("PAY-1001", "ORD-1001", "CUST-1001", 249.99, "credit_card", "successful", "TXN-1001992", "2026-08-05T10:01:00Z"),
            ("PAY-1002", "ORD-1002", "CUST-1001", 129.99, "paypal", "successful", "TXN-1002883", "2026-07-15T14:31:00Z"),
            ("PAY-1003", "ORD-1003", "CUST-1001", 99.99, "credit_card", "successful", "TXN-1003774", "2026-06-01T09:16:00Z"),
            ("PAY-1004", "ORD-1004", "CUST-1002", 129.99, "apple_pay", "successful", "TXN-1004665", "2026-08-02T11:21:00Z"),
            ("PAY-1005", "ORD-1005", "CUST-1003", 599.99, "credit_card", "successful", "TXN-1005556", "2026-08-01T15:01:00Z"),
            ("PAY-1006", "ORD-1006", "CUST-1003", 249.99, "credit_card", "refunded", "TXN-1006447", "2026-07-10T12:01:00Z"),
            ("PAY-1007", "ORD-1007", "CUST-1004", 89.99, "paypal", "successful", "TXN-1007338", "2026-07-25T16:31:00Z"),
            ("PAY-1008", "ORD-1008", "CUST-1005", 299.99, "credit_card", "pending", "TXN-1008229", "2026-08-06T09:46:00Z"),
            ("PAY-1009", "ORD-1009", "CUST-1005", 599.99, "credit_card", "successful", "TXN-1009110", "2026-07-01T10:01:00Z"),
            ("PAY-1010", "ORD-1010", "CUST-1005", 599.97, "credit_card", "refunded", "TXN-1010001", "2026-05-15T14:01:00Z"),
            ("PAY-1011", "ORD-1011", "CUST-1007", 299.99, "credit_card", "successful", "TXN-1011990", "2026-08-04T11:01:00Z"),
            ("PAY-1012", "ORD-1012", "CUST-1008", 249.99, "apple_pay", "successful", "TXN-1012889", "2026-08-03T13:16:00Z"),
            ("PAY-1013", "ORD-1015", "CUST-1011", 249.99, "credit_card", "successful", "TXN-1015554", "2026-08-02T15:46:00Z"),
            ("PAY-1014", "ORD-1016", "CUST-1013", 599.99, "credit_card", "successful", "TXN-1016443", "2026-08-05T12:31:00Z"),
            ("PAY-1015", "ORD-1018", "CUST-1016", 109.99, "paypal", "successful", "TXN-1018221", "2026-08-01T14:11:00Z"),
            ("PAY-1016", "ORD-1020", "CUST-1020", 249.99, "credit_card", "successful", "TXN-1020009", "2026-07-30T10:01:00Z"),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO payments
            (payment_id, order_id, customer_id, amount, payment_method, payment_status, transaction_reference, payment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, payments)

        # 7. Synthetic Shipments
        shipments = [
            ("SHIP-1001", "ORD-1001", "FedEx", "FX10012398", "in_transit", "2026-08-06T08:00:00Z", "2026-08-10", None),
            ("SHIP-1002", "ORD-1002", "UPS", "UPS9876543", "delivered", "2026-07-16T09:00:00Z", "2026-07-20", "2026-07-19T14:20:00Z"),
            ("SHIP-1003", "ORD-1004", "DHL", "DHL4561237", "label_created", "2026-08-03T10:00:00Z", "2026-08-12", None),
            ("SHIP-1004", "ORD-1005", "FedEx", "FX99887766", "delivered", "2026-08-02T08:30:00Z", "2026-08-06", "2026-08-05T11:15:00Z"),
            ("SHIP-1005", "ORD-1007", "USPS", "USPS776655", "delivered", "2026-07-26T10:00:00Z", "2026-07-30", "2026-07-29T16:00:00Z"),
            ("SHIP-1006", "ORD-1011", "UPS", "UPS55667788", "in_transit", "2026-08-05T09:00:00Z", "2026-08-09", None),
            ("SHIP-1007", "ORD-1012", "DHL", "DHL99881122", "delivered", "2026-08-04T11:00:00Z", "2026-08-07", "2026-08-07T13:40:00Z"),
            ("SHIP-1008", "ORD-1015", "FedEx", "FX44332211", "out_for_delivery", "2026-08-03T08:00:00Z", "2026-08-08", None),
            ("SHIP-1009", "ORD-1018", "DHL", "DHL66554433", "in_transit", "2026-08-02T10:00:00Z", "2026-08-07", None),
            ("SHIP-1010", "ORD-1020", "USPS", "USPS990011", "delivered", "2026-07-31T09:00:00Z", "2026-08-04", "2026-08-04T15:30:00Z"),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO shipments
            (shipment_id, order_id, carrier, tracking_number, shipment_status, shipped_at, estimated_delivery, delivered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, shipments)

        # 8. Synthetic Subscriptions
        subscriptions = [
            ("SUB-1001", "CUST-1001", "Pro Care Plan", "active", "monthly", "2024-02-01", "2026-09-01", 29.99),
            ("SUB-1002", "CUST-1003", "Enterprise Support Plan", "active", "annual", "2023-12-01", "2027-01-01", 299.99),
            ("SUB-1003", "CUST-1005", "Basic Care Plan", "active", "monthly", "2023-09-01", "2026-08-25", 9.99),
            ("SUB-1004", "CUST-1007", "Pro Care Plan", "cancelled", "monthly", "2024-02-01", "2026-06-01", 29.99),
            ("SUB-1005", "CUST-1008", "Pro Care Plan", "active", "monthly", "2024-01-01", "2026-09-01", 29.99),
            ("SUB-1006", "CUST-1011", "Basic Care Plan", "active", "annual", "2023-11-01", "2026-11-01", 99.99),
            ("SUB-1007", "CUST-1013", "Enterprise Support Plan", "active", "annual", "2023-10-01", "2026-10-01", 299.99),
            ("SUB-1008", "CUST-1018", "VIP Priority Plan", "active", "monthly", "2023-08-01", "2026-09-01", 49.99),
            ("SUB-1009", "CUST-1020", "Pro Care Plan", "paused", "monthly", "2024-01-01", "2026-08-15", 29.99),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO subscriptions
            (subscription_id, customer_id, plan, status, billing_cycle, start_date, renewal_date, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, subscriptions)

        conn.commit()
        logger.info("Company business database seeded successfully with 22 synthetic customers.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to seed company database: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed_company_database()
