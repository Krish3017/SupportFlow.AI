import asyncio
import logging
import sqlite3
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging with ASCII format
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_company_data")

from company_data.connection import get_company_db_connection, get_company_db_path
from company_data.seed import seed_company_database
from company_data.service import CompanyDataService
from company_data.tools import (
    get_customer_by_email,
    get_customer_by_id,
    get_customer_orders,
    get_order_details,
    get_order_status,
    get_shipment_status,
    get_payment_status,
    get_product_details,
    get_customer_subscription,
)
from agents.company_data_agent import company_data_agent_node
from apps.chat.router import workflow


def run_unit_tests():
    print("==================================================")
    print("RUNNING COMPANY DATA LAYER & TOOLS UNIT TESTS")
    print("==================================================")

    # Remove old database file if exists to ensure clean slate
    db_path = get_company_db_path()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    # Ensure database seeded
    seed_company_database()
    service = CompanyDataService()

    # Test 1: Find customer by email
    res1 = get_customer_by_email("alice.johnson@example.com")
    assert res1["found"] is True, "Test 1 Failed: Customer by email not found"
    assert res1["customer"]["customer_id"] == "CUST-1001"
    print("[PASS] Test 1: Find customer by email")

    # Test 2: Find customer by ID
    res2 = get_customer_by_id("CUST-1002")
    assert res2["found"] is True, "Test 2 Failed: Customer by ID not found"
    assert res2["customer"]["email"] == "bob.smith@example.com"
    print("[PASS] Test 2: Find customer by ID")

    # Test 3: Retrieve customer's orders
    res3 = get_customer_orders("CUST-1001", limit=5)
    assert res3["found"] is True, "Test 3 Failed: Customer orders not found"
    assert len(res3["orders"]) >= 1
    print("[PASS] Test 3: Retrieve customer's orders")

    # Test 4: Retrieve order details
    res4 = get_order_details("ORD-1001")
    assert res4["found"] is True, "Test 4 Failed: Order details not found"
    assert res4["order"]["customer_id"] == "CUST-1001"
    assert len(res4["items"]) >= 1
    print("[PASS] Test 4: Retrieve order details")

    # Test 5: Retrieve shipment status
    res5 = get_shipment_status("ORD-1001")
    assert res5["found"] is True, "Test 5 Failed: Shipment status not found"
    assert res5["carrier"] == "FedEx"
    print("[PASS] Test 5: Retrieve shipment status")

    # Test 6: Retrieve payment status
    res6 = get_payment_status("ORD-1001")
    assert res6["found"] is True, "Test 6 Failed: Payment status not found"
    assert res6["payment_status"] == "successful"
    print("[PASS] Test 6: Retrieve payment status")

    # Test 7: Retrieve product details
    res7 = get_product_details("PROD-101")
    assert res7["found"] is True, "Test 7 Failed: Product details not found"
    assert res7["product"]["product_name"] == "Wireless Noise-Canceling Headphones"
    print("[PASS] Test 7: Retrieve product details")

    # Test 8: Retrieve subscription
    res8 = get_customer_subscription("alice.johnson@example.com")
    assert res8["found"] is True, "Test 8 Failed: Subscription not found"
    assert res8["subscription"]["plan"] == "Pro Care Plan"
    print("[PASS] Test 8: Retrieve subscription")

    # Test 9: Invalid customer
    res9 = get_customer_by_id("CUST-999999")
    assert res9["found"] is False, "Test 9 Failed: Invalid customer should return found=False"
    print("[PASS] Test 9: Invalid customer handled correctly")

    # Test 10: Invalid order
    res10 = get_order_details("ORD-999999")
    assert res10["found"] is False, "Test 10 Failed: Invalid order should return found=False"
    print("[PASS] Test 10: Invalid order handled correctly")

    # Test 11: Verify foreign-key relationships
    conn = get_company_db_connection()
    try:
        # Check every order belongs to existing customer
        orphan_orders = conn.execute("""
            SELECT o.order_id FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """).fetchall()
        assert len(orphan_orders) == 0, "Test 11 Failed: Found orphan orders without valid customer FK"

        # Check order_items reference valid order and product
        orphan_items = conn.execute("""
            SELECT oi.item_id FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE o.order_id IS NULL OR p.product_id IS NULL
        """).fetchall()
        assert len(orphan_items) == 0, "Test 11 Failed: Found orphan order items without valid FKs"
        print("[PASS] Test 11: Foreign-key relationships intact")
    finally:
        conn.close()

    # Test 12: Verify agents/tools can retrieve company data
    async def test_agent_node():
        state = {
            "customer_message": "Where is order ORD-1001?",
            "intent": "order_status",
            "customer_id": "alice.johnson@example.com",
        }
        res_node = await company_data_agent_node(state)
        assert res_node.get("company_data_context") is not None
        assert "ORD-1001" in res_node["company_data_context"]
        print("[PASS] Test 12: Company Data Agent node successfully retrieved context")

    asyncio.run(test_agent_node())


async def run_e2e_scenarios():
    print("\n==================================================")
    print("RUNNING END-TO-END WORKFLOW SCENARIOS")
    print("==================================================")

    scenarios = [
        {
            "name": "Scenario 1: 'Where is my order?'",
            "message": "Where is my order?",
            "customer_id": "alice.johnson@example.com",
        },
        {
            "name": "Scenario 2: 'What is the status of order ORD-1005?'",
            "message": "What is the status of order ORD-1005?",
            "customer_id": "carol.williams@example.com",
        },
        {
            "name": "Scenario 3: 'Did my payment succeed?'",
            "message": "Did my payment succeed for order ORD-1001?",
            "customer_id": "alice.johnson@example.com",
        },
        {
            "name": "Scenario 4: 'What is your refund policy?' (RAG verification)",
            "message": "What is your refund policy?",
            "customer_id": "alice.johnson@example.com",
        },
        {
            "name": "Scenario 5: 'Tell me about my subscription.'",
            "message": "Tell me about my subscription.",
            "customer_id": "alice.johnson@example.com",
        },
    ]

    for sc in scenarios:
        print(f"\n--- {sc['name']} ---")
        print(f"User ({sc['customer_id']}): {sc['message']}")

        result = await workflow.ainvoke({
            "customer_message": sc["message"],
            "customer_id": sc["customer_id"],
            "session_id": "test_session_e2e",
            "chat_history": []
        })

        resp = result.get("final_response", "No response")
        comp_ctx = result.get("company_data_context")
        rag_ctx = result.get("retrieved_context")

        print(f"Company Data Queried: {'Yes' if comp_ctx else 'No'}")
        if comp_ctx:
            print(f"Company Context Snippet: {comp_ctx[:150]}...")
        if rag_ctx:
            print(f"RAG Context Snippet: {rag_ctx[:150]}...")
        print(f"AI Response Snippet: {resp[:200]}...")


if __name__ == "__main__":
    run_unit_tests()
    asyncio.run(run_e2e_scenarios())
