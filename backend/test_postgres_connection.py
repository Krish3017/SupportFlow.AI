"""
PostgreSQL Connection Test Suite
Verifies connection, version, schemas, tables, and row counts on Supabase PostgreSQL.
"""
import sys
import os

# Ensure backend root directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from core.postgres import get_postgres_connection
from core.config import settings

def run_test():
    print("==================================================")
    print("SUPPORTFLOW AI - SUPABASE POSTGRESQL TEST SUITE")
    print("==================================================")

    if not settings.DATABASE_URL:
        print("[ERROR] DATABASE_URL is not set in environment!")
        sys.exit(1)

    print("[1] Connecting to Supabase PostgreSQL...")
    conn = get_postgres_connection()
    print("    -> Connection established successfully.")

    try:
        with conn.cursor() as cur:
            # 2. Get PostgreSQL Version
            cur.execute("SELECT version();")
            ver = cur.fetchone()
            print(f"[2] PostgreSQL Version:\n    {ver['version']}")

            # 3. Get Current Database Name
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()
            print(f"[3] Current Database: {db_name['current_database']}")

            # 4. Verify Schemas
            print("[4] Verifying Target Schemas...")
            cur.execute("""
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name IN ('supportflow', 'company')
                ORDER BY schema_name;
            """)
            schemas = [r['schema_name'] for r in cur.fetchall()]
            print(f"    -> Schemas found: {schemas}")
            assert 'company' in schemas, "Schema 'company' is missing!"
            assert 'supportflow' in schemas, "Schema 'supportflow' is missing!"

            # 5. Verify Target Tables
            print("[5] Verifying Target Tables...")
            expected_tables = {
                'supportflow': [
                    'customers', 'customer_sessions', 'conversations',
                    'messages', 'executions', 'execution_steps', 'tickets'
                ],
                'company': [
                    'customers', 'orders', 'order_items',
                    'payments', 'shipments', 'subscriptions'
                ]
            }

            for schema, tables in expected_tables.items():
                for table in tables:
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = %s AND table_name = %s;
                    """, (schema, table))
                    res = cur.fetchone()
                    assert res is not NULL if False else res is not None, f"Table {schema}.{table} not found!"
                    print(f"    [OK] {schema}.{table}")

            # 6. Perform Harmless Row Count Queries
            print("[6] Executing Row Count Checks...")
            cur.execute("SELECT COUNT(*) AS count FROM supportflow.customers;")
            sf_cust_count = cur.fetchone()['count']
            print(f"    -> supportflow.customers count: {sf_cust_count}")

            cur.execute("SELECT COUNT(*) AS count FROM company.customers;")
            comp_cust_count = cur.fetchone()['count']
            print(f"    -> company.customers count: {comp_cust_count}")

            print("\n==================================================")
            print("ALL POSTGRESQL VERIFICATION TESTS PASSED SUCCESSFULLY!")
            print("==================================================")
    finally:
        conn.close()
        print("[7] Connection cleanly closed.")

if __name__ == "__main__":
    run_test()
