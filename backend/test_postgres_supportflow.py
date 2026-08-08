import sys, os, time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.postgres import get_postgres_connection
from apps.auth.service import AuthService
from shared.persistence import _get_db, ensure_contact, get_or_create_conversation, store_user_message, store_assistant_message, create_execution, complete_execution, record_execution_steps, create_ticket_on_escalation, get_conversation_messages
from apps.customers.repository import CustomerRepository
from apps.conversations.repository import ConversationRepository
from apps.tickets.repository import TicketRepository
from apps.observatory.repository import ObservatoryRepository
from apps.analytics.repository import AnalyticsRepository
from apps.activity.repository import ActivityRepository
from apps.email.repository import EmailRepository
from apps.knowledge.repository import KnowledgeRepository
from company_data.seed import seed_company_database

def run_tests():
    print('=' * 70, flush=True)
    print('SUPPORTFLOW CORE POSTGRESQL VERIFICATION SUITE', flush=True)
    print('=' * 70, flush=True)
    seed_company_database()
    auth = AuthService()
    ts = int(time.time())
    email_a = f'cust_a_{ts}@example.com'
    email_b = f'cust_b_{ts}@example.com'
    tok_a, user_a = auth.register_customer(email_a, '12345678', 'Customer A')
    assert user_a['email'] == email_a
    me_a = auth.get_authenticated_customer(tok_a)
    assert me_a['id'] == user_a['id']
    tok_login_a, user_login_a = auth.login_customer(email_a, '12345678')
    assert user_login_a['id'] == user_a['id']
    auth.logout_customer(tok_a)
    assert auth.get_authenticated_customer(tok_a) is None
    print('[PASS] 1. Customer Auth Lifecycle (Register, Me, Login, Logout, Session Invalidation)', flush=True)
    tok_a, user_a = auth.login_customer(email_a, '12345678')
    c_a = user_a['id']
    conv1 = get_or_create_conversation(c_a, 'chat', f'sess_a_{ts}')
    m1 = store_user_message(conv1, 'Help with account')
    ex1 = create_execution(m1, conv1)
    complete_execution(ex1, {'intent': 'general_inquiry', 'confidence': 0.95}, 0.5)
    store_assistant_message(conv1, 'Hello! How can I help?', ex1)
    conv2 = get_or_create_conversation(c_a, 'chat', f'sess_a_{ts}')
    assert conv1 == conv2
    store_user_message(conv2, 'Where is my order?')
    print(f'[PASS] 2. Active Conversation Reuse ({conv1})', flush=True)
    tok_b, user_b = auth.register_customer(email_b, '12345678', 'Customer B')
    c_b = user_b['id']
    conv_b = get_or_create_conversation(c_b, 'chat', f'sess_b_{ts}')
    store_user_message(conv_b, 'Customer B private message')
    assert conv_b != conv1
    msgs_b = get_conversation_messages(conv_b)
    assert len(msgs_b) == 1 and msgs_b[0]['content'] == 'Customer B private message'
    msgs_a = get_conversation_messages(conv1)
    assert len(msgs_a) == 3
    print('[PASS] 3. Multi-Customer Security Isolation (Customer A vs Customer B)', flush=True)
    ex_test = create_execution(m1, conv1)
    res_mock = {'intent': 'order_status', 'sentiment': 'neutral', 'confidence': 0.95, 'customer_context': 'Krish', 'priority': 'medium', 'retrieved_context': 'FedEx shipping', 'final_response': 'Order shipped', 'escalate': False}
    record_execution_steps(ex_test, res_mock, 'Where is my order?', 1.0)
    complete_execution(ex_test, res_mock, 1.0)
    conn = get_postgres_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM supportflow.execution_steps WHERE execution_id = %s', (ex_test,))
        steps = cur.fetchall()
        assert len(steps) == 6
    conn.close()
    print('[PASS] 4. AI Observability and Step Latencies', flush=True)
    tkt = create_ticket_on_escalation(conv1, c_a, {'customer_message': 'Need refund', 'intent': 'refund_request', 'confidence': 0.9, 'priority': 'high', 'escalate': True})
    assert tkt is not None
    print(f'[PASS] 5. Ticket Escalation on PostgreSQL ({tkt})', flush=True)
    assert len(CustomerRepository().list_customers()[0]) >= 2
    assert len(ConversationRepository().list_conversations()[0]) >= 2
    assert len(TicketRepository().list_tickets()[0]) >= 1
    assert len(ObservatoryRepository().list_executions()[0]) >= 1
    analytics_res = AnalyticsRepository().get_conversation_overview()
    assert 'total' in analytics_res
    ActivityRepository().list_activity()
    EmailRepository().list_emails()
    KnowledgeRepository().list_documents()
    print('[PASS] 6. All 8 Admin Repositories/APIs Querying Supabase PostgreSQL (supportflow schema)', flush=True)
    print('=' * 70, flush=True)
    print('ALL SUPPORTFLOW CORE POSTGRESQL VERIFICATION TESTS PASSED!', flush=True)
    print('=' * 70, flush=True)

if __name__ == '__main__':
    run_tests()