import asyncio
import os
import sys
import logging
import sqlite3

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging with ASCII format
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_auth_identity")

from database import create_tables
from company_data.seed import seed_company_database
from company_data.connection import get_company_db_path
from company_data.service import CompanyDataService
from apps.auth.service import AuthService, hash_password, verify_password
from agents.company_data_agent import company_data_agent_node
from telegram_bot import process_through_workflow
from apps.chat.router import workflow
from shared.persistence import _get_db, ensure_contact, link_contact_company_customer


def run_auth_identity_tests():
    print("==================================================")
    print("RUNNING SUPPORTFLOW AUTH & IDENTITY TEST SUITE")
    print("==================================================")

    # Clean and seed databases
    create_tables()
    conn = _get_db()
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM customer_sessions")
        conn.execute("DELETE FROM customers WHERE email LIKE '%test%' OR email IN ('alice.johnson@example.com', 'carol.williams@example.com')")
        conn.execute("DELETE FROM contact_channels WHERE contact_id LIKE '%tg_user%' OR contact_id LIKE '%alice%' OR contact_id LIKE '%carol%' OR contact_id LIKE '%test%'")
        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")
    finally:
        conn.close()

    seed_company_database()
    auth_service = AuthService()

    # ----------------------------------------------------
    # Test 1: Customer Registration
    # ----------------------------------------------------
    test_email = "test.user@example.com"
    token1, user1 = auth_service.register_customer(test_email, "securepass123", "Test User")
    assert token1 is not None and token1.startswith("sf_sess_"), "Test 1 Failed: Token invalid"
    assert user1["email"] == test_email, "Test 1 Failed: Email mismatch"
    print("[PASS] Test 1: Customer registration successful")

    # ----------------------------------------------------
    # Test 2: Password Hashing & Verification
    # ----------------------------------------------------
    raw_password = "mySecretPassword99"
    hashed = hash_password(raw_password)
    assert hashed != raw_password, "Test 2 Failed: Password not hashed"
    assert "$" in hashed, "Test 2 Failed: Salt missing from hash format"
    assert verify_password(raw_password, hashed) is True, "Test 2 Failed: Password verification failed"
    assert verify_password("wrongPassword", hashed) is False, "Test 2 Failed: Invalid password verified"
    print("[PASS] Test 2: Password hashing & verification robust")

    # ----------------------------------------------------
    # Test 3: Login
    # ----------------------------------------------------
    token3, user3 = auth_service.login_customer(test_email, "securepass123")
    assert token3 is not None, "Test 3 Failed: Login token missing"
    assert user3["email"] == test_email, "Test 3 Failed: Login user mismatch"
    print("[PASS] Test 3: Customer login successful")

    # ----------------------------------------------------
    # Test 4: Logout / Session Invalidation
    # ----------------------------------------------------
    assert auth_service.logout_customer(token3) is True, "Test 4 Failed: Logout failed"
    assert auth_service.get_authenticated_customer(token3) is None, "Test 4 Failed: Session active after logout"
    print("[PASS] Test 4: Logout & session invalidation verified")

    # ----------------------------------------------------
    # Test 5: Authenticated Customer Retrieval
    # ----------------------------------------------------
    token5, _ = auth_service.login_customer(test_email, "securepass123")
    auth_user = auth_service.get_authenticated_customer(token5)
    assert auth_user is not None, "Test 5 Failed: Authenticated customer not found"
    assert auth_user["email"] == test_email, "Test 5 Failed: Authenticated retrieval email mismatch"
    print("[PASS] Test 5: Authenticated customer retrieval verified")

    # ----------------------------------------------------
    # Test 6: Contact Creation & Linking
    # ----------------------------------------------------
    contact_id6 = ensure_contact("alice.johnson@example.com", "chat")
    conn = _get_db()
    row6 = conn.execute("SELECT company_customer_id FROM customers WHERE id = ?", (contact_id6,)).fetchone()
    conn.close()
    assert row6 is not None, "Test 6 Failed: Contact record not found in SupportFlow DB"
    print("[PASS] Test 6: Contact creation & DB persistence verified")

    # ----------------------------------------------------
    # Test 7: Company Customer Matching by Exact Email
    # ----------------------------------------------------
    # Register customer with company email "alice.johnson@example.com"
    token7, user7 = auth_service.register_customer("alice.johnson@example.com", "alicepass123", "Alice Johnson")
    assert user7["company_customer_id"] == "CUST-1001", f"Test 7 Failed: Company customer ID expected CUST-1001, got {user7['company_customer_id']}"
    print("[PASS] Test 7: Company customer matched by exact email (CUST-1001)")

    # ----------------------------------------------------
    # Test 8: Telegram Identity Linking
    # ----------------------------------------------------
    async def test_telegram_linking():
        tg_user_id = "tg_user_888999"

        # Step A: Unlinked message for account data prompts for email
        resp_prompt = await process_through_workflow(None, "Where is my order?", tg_user_id, "tg_sess_1")
        assert "provide the email associated with your account" in resp_prompt, "Test 8 Failed: Did not prompt for email"

        # Step B: User responds with exact email "carol.williams@example.com"
        resp_link = await process_through_workflow(None, "carol.williams@example.com", tg_user_id, "tg_sess_1")
        assert "linked successfully" in resp_link, f"Test 8 Failed: Linking failed response: {resp_link}"

        # Verify linked in DB
        contact_id_tg = ensure_contact(tg_user_id, "telegram")
        conn = _get_db()
        row_tg = conn.execute("SELECT company_customer_id FROM customers WHERE id = ?", (contact_id_tg,)).fetchone()
        conn.close()
        assert row_tg["company_customer_id"] == "CUST-1003", f"Test 8 Failed: Expected CUST-1003, got {row_tg['company_customer_id']}"

        print("[PASS] Test 8: Telegram identity linked via email prompt to CUST-1003")

    asyncio.run(test_telegram_linking())

    # ----------------------------------------------------
    # Test 9: Telegram Identity Persistence
    # ----------------------------------------------------
    async def test_telegram_persistence():
        tg_user_id = "tg_user_888999"
        # Submitting second order query from same Telegram user -> must NOT ask for email again!
        resp_second = await process_through_workflow(None, "Where is my order?", tg_user_id, "tg_sess_2")
        assert "provide the email associated" not in resp_second, "Test 9 Failed: Email requested again"
        assert any(kw in resp_second.lower() for kw in ["ord-", "delivered", "order", "shipment", "status"]), f"Test 9 Failed: Response did not include order info: {resp_second}"
        print("[PASS] Test 9: Telegram identity persisted without re-asking email")

    asyncio.run(test_telegram_persistence())

    # ----------------------------------------------------
    # Test 10: Unresolved Customer
    # ----------------------------------------------------
    async def test_unresolved():
        state_unresolved = {
            "customer_message": "Where is my order?",
            "intent": "order_status",
            "customer_id": "anon_unresolved_999",
        }
        node_res = await company_data_agent_node(state_unresolved)
        ctx = node_res.get("company_data_context", "")
        assert "Identity Unresolved" in ctx, "Test 10 Failed: Unresolved identity allowed access"
        print("[PASS] Test 10: Unresolved customer blocked from company data access")

    asyncio.run(test_unresolved())

    # ----------------------------------------------------
    # Test 11: Authorized Scoped Access - Customer Can Retrieve Own Orders
    # ----------------------------------------------------
    async def test_own_orders():
        state_alice = {
            "customer_message": "Where is my order?",
            "intent": "order_status",
            "customer_id": "alice.johnson@example.com",
            "company_customer": {"customer_id": "CUST-1001", "name": "Alice Johnson"},
        }
        res_alice = await company_data_agent_node(state_alice)
        ctx = res_alice.get("company_data_context", "")
        assert "CUST-1001" in ctx, "Test 11 Failed: Alice's customer ID not in context"
        assert "ORD-1001" in ctx, "Test 11 Failed: Alice's order ORD-1001 missing"
        print("[PASS] Test 11: Customer can retrieve own orders")

    asyncio.run(test_own_orders())

    # ----------------------------------------------------
    # Test 12: Customer Cannot Retrieve Another Customer's Orders
    # ----------------------------------------------------
    async def test_other_customer_orders():
        state_alice_asking_bob = {
            "customer_message": "What are Bob Smith's orders?",
            "intent": "order_status",
            "customer_id": "alice.johnson@example.com",
            "company_customer": {"customer_id": "CUST-1001", "name": "Alice Johnson"},
        }
        res_ask_bob = await company_data_agent_node(state_alice_asking_bob)
        ctx = res_ask_bob.get("company_data_context", "")
        assert "CUST-1002" not in ctx, "Test 12 Failed: Bob's CUST-1002 data returned to Alice!"
        assert "bob.smith" not in ctx.lower(), "Test 12 Failed: Bob's data leaked to Alice!"
        print("[PASS] Test 12: Customer cannot retrieve another customer's orders")

    asyncio.run(test_other_customer_orders())

    # ----------------------------------------------------
    # Test 13: Customer Cannot Access Another Customer's Order by ID
    # ----------------------------------------------------
    async def test_order_id_access_control():
        # ORD-1005 belongs to Carol (CUST-1003). Alice (CUST-1001) asks for ORD-1005.
        state_alice_asking_ord1005 = {
            "customer_message": "What is the status of order ORD-1005?",
            "intent": "order_status",
            "customer_id": "alice.johnson@example.com",
            "company_customer": {"customer_id": "CUST-1001", "name": "Alice Johnson"},
        }
        res_ord1005 = await company_data_agent_node(state_alice_asking_ord1005)
        ctx = res_ord1005.get("company_data_context", "")
        assert "was not found for your account" in ctx, f"Test 13 Failed: Access granted for foreign order! Ctx: {ctx}"
        assert "Ultra-Wide 4K Monitor" not in ctx, "Test 13 Failed: Foreign order line items leaked!"
        print("[PASS] Test 13: Customer cannot access another customer's order by ID")

    asyncio.run(test_order_id_access_control())

    # ----------------------------------------------------
    # Test 14: Email Sender Matching
    # ----------------------------------------------------
    email_contact = ensure_contact("alice.johnson@example.com", "email")
    conn = _get_db()
    row_email = conn.execute("SELECT company_customer_id FROM customers WHERE id = ?", (email_contact,)).fetchone()
    conn.close()
    assert row_email["company_customer_id"] == "CUST-1001", "Test 14 Failed: Email sender matching failed"
    print("[PASS] Test 14: Email sender matching automatically resolved CUST-1001")

    # ----------------------------------------------------
    # Test 15: Session Persistence Across Calls
    # ----------------------------------------------------
    token15, _ = auth_service.login_customer("test.user@example.com", "securepass123")
    user15_a = auth_service.get_authenticated_customer(token15)
    user15_b = auth_service.get_authenticated_customer(token15)
    assert user15_a is not None and user15_a["id"] == user15_b["id"], "Test 15 Failed: Session persistence failed"
    print("[PASS] Test 15: Session persistence across calls verified")


if __name__ == "__main__":
    run_auth_identity_tests()
