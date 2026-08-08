# SUPPORTFLOW AI — COMPLETE DATA & API AUDIT

---

## CURRENT ARCHITECTURE

Two isolated SQLite databases. FastAPI backend with LangGraph multi-agent orchestration. Next.js admin panel. Three support channels: Web Chat (SSE streaming), Email (Gmail polling), Telegram (implied by channel value in DB, not directly visible in this codebase slice).

**Database files:**
- `supportflow.db` — SupportFlow operational database (path from `DATABASE_PATH` env var)
- `company_data.db` — Simulated company business database (path from `COMPANY_DATABASE_PATH` env var)

---

## SUPPORTFLOW DATABASE

### Tables

**`customers`** (the SupportFlow "Contact" record)
```
id                   TEXT PK          (format: cust_<hex12> or email-derived)
name                 TEXT             nullable
email                TEXT UNIQUE NOT NULL
password_hash        TEXT             nullable — PBKDF2-HMAC-SHA256, salt$hash
company_customer_id  TEXT             nullable — FK link to company_data.db
tier                 TEXT DEFAULT 'standard'
sentiment            TEXT DEFAULT 'neutral'
total_conversations  INTEGER DEFAULT 0
resolved_conversations INTEGER DEFAULT 0
avg_response_time    REAL DEFAULT 0.0
interaction_frequency TEXT            nullable — never populated
last_interaction     TEXT             ISO timestamp
joined_date          TEXT NOT NULL    ISO timestamp
risk_score           INTEGER DEFAULT 0  — never populated, always 0
lifetime_value       REAL DEFAULT 0.0   — never populated, always 0.0
tags                 TEXT             nullable — comma-separated string
```
Indexes: email, tier, company_customer_id
Written by: `shared/persistence.py::ensure_contact()`, `auth/service.py::register_customer()`
Read by: `apps/customers/`, `apps/auth/`, `agents/customer_intelligence_agent.py`

---

**`customer_sessions`**
```
session_token  TEXT PK     (format: sf_sess_<uuid_hex>)
customer_id    TEXT NOT NULL FK → customers.id CASCADE DELETE
created_at     TEXT NOT NULL
expires_at     TEXT NOT NULL  (7 days)
```
Indexes: session_token
Written by: `auth/service.py::_create_session()`
Read by: `auth/service.py::get_authenticated_customer()`
**No expiry enforcement** — sessions never purged even after expires_at passes.

---

**`contact_channels`**
```
id                 INTEGER PK AUTOINCREMENT
contact_id         TEXT NOT NULL FK → customers.id
channel_type       TEXT NOT NULL   (chat, email, telegram)
channel_identifier TEXT NOT NULL   (format: "channel:contact_id")
verified           INTEGER DEFAULT 0  — always 0, never verified
created_at         TEXT NOT NULL
UNIQUE(channel_type, channel_identifier)
```
Indexes: contact_id, (channel_type, channel_identifier)
Written by: `shared/persistence.py::ensure_contact()`
Read by: nobody currently — no repository or API queries this table.

---

**`conversations`**
```
id            TEXT PK     (format: conv_<hex12>)
contact_id    TEXT NOT NULL FK → customers.id
channel       TEXT NOT NULL  (chat, email, telegram)
status        TEXT DEFAULT 'active'  (active, resolved, escalated, closed)
subject       TEXT            nullable — never populated
started_at    TEXT NOT NULL
updated_at    TEXT NOT NULL
resolved_at   TEXT            nullable
closed_at     TEXT            nullable
session_token TEXT            nullable — session_id for web chat
metadata      TEXT            nullable — never populated
```
Indexes: contact_id, status, channel, session_token, updated_at
Written by: `shared/persistence.py::get_or_create_conversation()`
Read by: `apps/conversations/`, `apps/tickets/` (via JOIN), `apps/customers/` (via sub-query)

---

**`messages`**
```
id              TEXT PK     (format: msg_<hex12>)
conversation_id TEXT NOT NULL FK → conversations.id
role            TEXT NOT NULL  (user, assistant)
content         TEXT NOT NULL
timestamp       TEXT NOT NULL
execution_id    TEXT            nullable FK → executions.id
metadata        TEXT            nullable
```
Indexes: conversation_id, timestamp, execution_id
Written by: `shared/persistence.py::store_user_message()`, `store_assistant_message()`
Read by: `apps/conversations/repository.py::get_messages()`

---

**`executions`**
```
id             TEXT PK     (format: exec_<hex12>)
message_id     TEXT NOT NULL FK → messages.id
conversation_id TEXT NOT NULL FK → conversations.id
status         TEXT DEFAULT 'running'  (running, completed, failed)
started_at     TEXT NOT NULL
completed_at   TEXT            nullable
total_duration REAL            nullable
confidence     REAL            nullable
intent         TEXT            nullable
sentiment      TEXT            nullable
priority       TEXT            nullable
escalated      INTEGER DEFAULT 0
error          TEXT            nullable
metadata       TEXT            nullable
```
Indexes: message_id, conversation_id, status, started_at
Written by: `shared/persistence.py::create_execution()`, `complete_execution()`
Read by: `apps/observatory/repository.py`

---

**`execution_steps`**
```
id             TEXT PK     (format: <exec_id>_step<N>)
execution_id   TEXT NOT NULL FK → executions.id
agent_id       TEXT NOT NULL   (intent_agent, customer_intelligence_agent, etc.)
agent_name     TEXT NOT NULL
sequence_order INTEGER NOT NULL
status         TEXT NOT NULL  (success, failed)
input_data     TEXT            nullable (truncated to 200 chars)
output_data    TEXT            nullable (truncated to 200/500 chars)
latency        REAL            nullable — approximated as total/count, not real per-agent latency
cost           REAL DEFAULT 0.0 — always 0.0, never calculated
error          TEXT            nullable
started_at     TEXT NOT NULL   — same for all steps (not real per-step timing)
completed_at   TEXT            nullable
```
Indexes: execution_id, agent_id
Written by: `shared/persistence.py::record_execution_steps()`
Read by: `apps/observatory/repository.py`

---

**`tickets`**
```
id               TEXT PK     (format: TKT_<hex12>)
conversation_id  TEXT NOT NULL FK → conversations.id
contact_id       TEXT NOT NULL FK → customers.id
subject          TEXT NOT NULL
priority         TEXT DEFAULT 'medium'
status           TEXT DEFAULT 'open'  (open, in_progress, resolved, escalated, closed)
assignee         TEXT            nullable
created_at       TEXT NOT NULL
updated_at       TEXT NOT NULL
resolved_at      TEXT            nullable
escalation_reason TEXT           nullable
metadata         TEXT            nullable
```
Indexes: conversation_id, contact_id, status, priority
Written by: `shared/persistence.py::create_ticket_on_escalation()` — **only created on escalation**
Read by: `apps/tickets/repository.py`, `apps/customers/repository.py`

---

**`activity_logs`**
```
id        INTEGER PK AUTOINCREMENT
type      TEXT NOT NULL  (system, agent, email, security, ticket, customer, conversation)
level     TEXT NOT NULL  (info, warning, error, critical)
message   TEXT NOT NULL
timestamp TEXT NOT NULL
metadata  TEXT            nullable — JSON
```
Indexes: type, timestamp
Written by: `shared/persistence.py::emit_activity()`, called from chat router and email agent
Read by: `apps/activity/repository.py`

---

**`knowledge_documents`**
```
id                TEXT PK     (UUID)
title             TEXT NOT NULL
type              TEXT NOT NULL  (pdf, txt, md)
status            TEXT NOT NULL  (indexed, pending, failed)
chunks            INTEGER DEFAULT 0
retrieval_count   INTEGER DEFAULT 0
last_updated      TEXT NOT NULL
size_bytes        INTEGER         nullable
file_path         TEXT            nullable — never populated for text uploads
chroma_collection TEXT            nullable — always 'default'
```
Indexes: status
Written by: `apps/knowledge/repository.py::create_document()`
Read by: `apps/knowledge/repository.py`, `apps/analytics/repository.py`
**No chunks table** — chunks live only in ChromaDB, not SQLite.

---

**`email_tickets`**
```
id               INTEGER PK AUTOINCREMENT
gmail_message_id TEXT UNIQUE     — deduplication key
sender_email     TEXT
subject          TEXT
body             TEXT
status           TEXT DEFAULT 'pending'  (pending, processing, resolved, escalated, error)
ai_response      TEXT            nullable
conversation_id  TEXT            nullable FK → conversations.id
created_at       TEXT
```
Written by: `database.py::save_email_ticket()`, `update_email_ticket()`
Read by: `apps/email/repository.py`
**`ticket_id` column is in the EmailResponse schema but does NOT exist in the database schema.** The `EmailDetailResponse` has a `linked_ticket` field but the service always returns `None` for it.

---

### SupportFlow DB Relationships Summary
```
customers 1──────────────────────── N customer_sessions
customers 1──────────────────────── N contact_channels
customers 1──────────────────────── N conversations
conversations 1──────────────────── N messages
conversations 1──────────────────── 1 tickets (escalation only)
messages 1──────────────────────── N executions (1 per message in practice)
executions 1──────────────────────── N execution_steps
email_tickets 0..1──────────────── 1 conversations (optional link)
knowledge_documents (standalone — vector data in ChromaDB)
activity_logs (standalone event log)
```

---

## COMPANY DATABASE

### Tables (in `company_data.db`)

**`customers`** (company business customers — NOT SupportFlow contacts)
```
customer_id       TEXT PK    (format: CUST-XXXX)
name              TEXT NOT NULL
email             TEXT UNIQUE NOT NULL
phone             TEXT
customer_tier     TEXT DEFAULT 'Bronze'  (Bronze, Silver, Gold, Platinum, VIP)
account_status    TEXT DEFAULT 'active'  (active, suspended, inactive)
registration_date TEXT NOT NULL
total_orders      INTEGER DEFAULT 0
total_spent       REAL DEFAULT 0.0
preferred_channel TEXT DEFAULT 'email'
created_at        TEXT NOT NULL
updated_at        TEXT NOT NULL
```

**`addresses`**
```
address_id    TEXT PK
customer_id   TEXT NOT NULL FK → customers.customer_id CASCADE
address_type  TEXT DEFAULT 'shipping'
street        TEXT NOT NULL
city, state, postal_code, country TEXT NOT NULL
is_default    INTEGER DEFAULT 0
created_at, updated_at TEXT
```

**`products`** (12 seeded: electronics, furniture, accessories)
```
product_id    TEXT PK    (format: PROD-XXX)
product_name  TEXT NOT NULL
description   TEXT
category      TEXT NOT NULL
price         REAL NOT NULL
stock_status  TEXT DEFAULT 'in_stock'  (in_stock, out_of_stock)
active_status INTEGER DEFAULT 1
created_at, updated_at TEXT
```

**`orders`** (22 seeded)
```
order_id               TEXT PK    (format: ORD-XXXX)
customer_id            TEXT NOT NULL FK → customers CASCADE
order_date             TEXT NOT NULL
status                 TEXT NOT NULL  (pending, confirmed, processing, shipped, delivered, returned, cancelled)
total_amount           REAL NOT NULL
currency               TEXT DEFAULT 'USD'
shipping_address_id    TEXT FK → addresses SET NULL
expected_delivery_date TEXT
actual_delivery_date   TEXT
tracking_information   TEXT
created_at, updated_at TEXT
```

**`order_items`**
```
item_id     TEXT PK
order_id    TEXT NOT NULL FK → orders CASCADE
product_id  TEXT NOT NULL FK → products RESTRICT
quantity    INTEGER NOT NULL
unit_price  REAL NOT NULL
total_price REAL NOT NULL
```

**`payments`**
```
payment_id           TEXT PK    (format: PAY-XXXX)
order_id             TEXT NOT NULL FK → orders CASCADE
customer_id          TEXT NOT NULL FK → customers CASCADE
amount               REAL NOT NULL
payment_method       TEXT NOT NULL  (credit_card, paypal, apple_pay)
payment_status       TEXT NOT NULL  (successful, pending, refunded, failed)
transaction_reference TEXT
payment_date         TEXT NOT NULL
```

**`shipments`**
```
shipment_id      TEXT PK    (format: SHIP-XXXX)
order_id         TEXT NOT NULL FK → orders CASCADE
carrier          TEXT NOT NULL  (FedEx, UPS, DHL, USPS)
tracking_number  TEXT NOT NULL
shipment_status  TEXT NOT NULL  (in_transit, delivered, label_created, out_for_delivery)
shipped_at       TEXT
estimated_delivery TEXT
delivered_at     TEXT
```

**`subscriptions`**
```
subscription_id TEXT PK    (format: SUB-XXXX)
customer_id     TEXT NOT NULL FK → customers CASCADE
plan            TEXT NOT NULL  (Basic Care Plan, Pro Care Plan, Enterprise Support Plan, VIP Priority Plan)
status          TEXT NOT NULL  (active, cancelled, paused)
billing_cycle   TEXT NOT NULL  (monthly, annual)
start_date, renewal_date TEXT NOT NULL
amount          REAL NOT NULL
```

23 seeded customers (CUST-1001 to CUST-1023), 12 products, 22 orders, 22 payments, 12 shipments, 10 subscriptions.

---

## DATABASE SEPARATION

**SUPPORTFLOW DB owns:**
- Support identity (customers table — email, password, tier, sentiment, session)
- Authentication (customer_sessions)
- Channel registrations (contact_channels)
- Conversation history (conversations, messages)
- AI execution traces (executions, execution_steps)
- Support tickets (tickets — escalation-only)
- Knowledge base metadata (knowledge_documents)
- Email intake (email_tickets)
- System audit log (activity_logs)

**COMPANY DB owns:**
- Business customer profiles (name, tier, contact info, spend history)
- Product catalog
- Orders / order items
- Payments
- Shipments
- Subscriptions
- Addresses

**The mapping is:**

```
SupportFlow customers.id  ──(company_customer_id FK)──▶  company_data.customers.customer_id
```

This is conceptually correct. The link is stored in `customers.company_customer_id` in SupportFlow DB. It is:
- Set on `register_customer()` if email matches a company customer
- Set on `login_customer()` same way
- Set lazily on `ensure_contact()` for any channel (chat/email)
- Callable via `link_contact_company_customer()`

**Duplication issue:** The SupportFlow `customers` table stores `tier`, `sentiment`, `risk_score`, `lifetime_value`, `interaction_frequency` — some of which overlap semantically with company DB `customer_tier`, `total_spent`. The SupportFlow `tier` and `lifetime_value` are never populated from actual data and default to `standard`/`0.0` for all new contacts, making the CustomerResponse `tier` and `lifetime_value` fields unreliable.

---

## IDENTITY FLOW

### Website (Web Chat)
```
POST /api/chat
  request.customer_id  ← from frontend (may be "anonymous" or email)
  authorization header ← sf_session token (if logged in)
    │
    ▼
AuthService.get_authenticated_customer(token)
    │  (if token present, overrides request.customer_id)
    ▼
ensure_contact(target_customer_id, "chat")
    │
    ├─ if ID exists in customers → update last_interaction
    ├─ if email → look up by email
    ├─ else → create new customer row (email: <id>@chat.supportflow)
    │
    └─ attempt company DB email match → link_contact_company_customer()
    ▼
get_or_create_conversation(contact_id, "chat", session_id)
    │  looks up by session_token (not closed/archived)
    └─ creates new conversation if not found
```

### Email
```
Gmail polling → email_agent._process_email(email)
    │
    ▼
ensure_contact(email["sender"], "email")
    │  sender is a real email → looks up or creates by email
    └─ attempts company DB email match
    ▼
get_or_create_conversation(contact_id, "email", session_id="email_<gmail_id>")
    │  one conversation per gmail message ID (no threading)
```

### Telegram
No Telegram-specific code is visible in the backend files inspected. The `channel` enum in schemas supports `telegram`, and `contact_channels` stores `channel_type`, but there is no Telegram bot handler found. The seed data references `preferred_channel: telegram` for some company customers, suggesting Telegram was planned or exists in a file not in this codebase slice.

---

## CONVERSATION FLOW

**One `session_id` → One `conversation` row** (looked up by `session_token`). Subsequent messages on the same session reuse the existing conversation. A new session creates a new conversation.

For web chat: `session_id` is generated by the frontend (UUID) and sent with each request. The chat router finds or creates the conversation by `session_token`.

For email: `session_id = f"email_{gmail_message_id}"` — so **each email creates a new conversation**, even from the same sender. There is no email threading.

**Conversation statuses** stored: `active`, `resolved`, `escalated`, `closed`.  
Escalation sets status to `escalated` via `create_ticket_on_escalation()`.  
Conversations are never automatically resolved — only escalated.

**Channel stored** in `conversations.channel` — correctly populated for chat and email.

---

## MESSAGE & EXECUTION FLOW

```
User message arrives
    ↓
store_user_message() → messages table (role='user')
    ↓
create_execution() → executions table (status='running')
    ↓
LangGraph workflow invoked:
  intent_agent → customer_intelligence_agent → priority_agent
      → company_data_agent
          → [conditional on intent] knowledge_agent → resolution_agent
          → [skip knowledge]        resolution_agent
      → escalation_agent
    ↓
record_execution_steps() → execution_steps table
  NOTE: ALL steps written at once after the workflow completes
  NOTE: latency = total_duration / step_count (approximation, not real)
  NOTE: started_at = completed_at = now (same timestamp for all steps)
  NOTE: cost = 0.0 always
    ↓
complete_execution() → executions table (status='completed')
    ↓
store_assistant_message() → messages table (role='assistant')
    ↓
create_ticket_on_escalation() → tickets table (only if escalate=True)
    ↓
update_contact_stats() → customers table
    ↓
emit_activity() → activity_logs table
```

---

## TICKET FLOW

Tickets are **only created on escalation** (`escalate=True` from `escalation_agent`). This happens when:
- `confidence < 0.6`
- `sentiment == "negative"` AND `intent == "complaint"`
- `sentiment == "negative"` AND `intent == "refund_request"`
- `intent == "legal_issue"`

Every conversation does NOT get a ticket. Most conversations have no ticket. The ticket subject is set from `customer_message` or `intent`, truncated to 100 chars. Ticket IDs use format `TKT_<hex12>`.

The admin panel's Tickets page correctly filters and shows only escalated conversations. The `TicketResponse.channel` field is derived from the JOIN with `conversations.channel` — correctly populated.

---

## COMPANY DATA FLOW

```
Agent node (company_data_agent_node)
    ↓
resolve_company_customer_id(state)
    │  checks state.company_customer → from customer_intelligence_agent
    │  fallback: query SupportFlow DB customers.company_customer_id
    │  fallback: query company DB by email
    ↓
tools.py function (e.g. get_order_details)
    ↓
CompanyDataService method (scoped)
    │  verifies company_customer_id ≠ None
    │  verifies order.customer_id == company_customer_id (ownership check)
    ↓
CompanyRepository (parameterized SQL)
    ↓
company_data.db
```

Customer scoping is enforced correctly in `service.py` for all account-specific methods. Product details are public (no customer scoping required). Identity is required before any account data is returned.

---

## COMPLETE ADMIN API INVENTORY

### Registered Routers (from main.py)

| Prefix | Tag |
|---|---|
| `/api/auth` | auth |
| `/api` | chat |
| `/api/admin/tickets` | tickets |
| `/api/admin/conversations` | conversations |
| `/api/admin/customers` | customers |
| `/api/admin/observatory` | observatory |
| `/api/admin/knowledge` | knowledge |
| `/api/admin/analytics` | analytics |
| `/api/admin/activity` | activity |
| `/api/admin/email` | email |

---

### AUTH

| Method | Route | Description |
|---|---|---|
| POST | `/api/auth/register` | Register customer, sets `sf_session` cookie |
| POST | `/api/auth/login` | Login, sets `sf_session` cookie |
| POST | `/api/auth/logout` | Logout, clears cookie |
| GET | `/api/auth/me` | Get authenticated customer |

---

### CHAT

| Method | Route | Description |
|---|---|---|
| POST | `/api/chat` | SSE streaming chat, full LangGraph invocation |
| GET | `/api/chat/history/{conversation_id}` | Raw message history |
| GET | `/api/chat/session/{session_id}` | Resolve session → conversation |

---

### TICKETS `/api/admin/tickets`

| Method | Route | Query Params | Notes |
|---|---|---|---|
| GET | `` | page, limit, status, priority, channel, search | Joins conversations + customers |
| GET | `/{ticket_id}` | — | Full detail with message_count |
| PATCH | `/{ticket_id}/status` | — | Body: `{status}` |

---

### CONVERSATIONS `/api/admin/conversations`

| Method | Route | Query Params |
|---|---|---|
| GET | `` | page, limit, customer_id, channel, status, ticket_id, search |
| GET | `/search` | q, limit |
| GET | `/{conversation_id}` | — |
| GET | `/{conversation_id}/messages` | — |

---

### CUSTOMERS `/api/admin/customers`

| Method | Route | Query Params |
|---|---|---|
| GET | `` | page, limit, tier, sentiment, min_risk_score, max_risk_score, search |
| GET | `/search` | q, limit |
| GET | `/{customer_id}` | — |
| GET | `/{customer_id}/tickets` | — |
| GET | `/{customer_id}/conversations` | — |

---

### OBSERVATORY `/api/admin/observatory`

| Method | Route | Query Params |
|---|---|---|
| GET | `/agents` | — |
| GET | `/agents/{agent_name}` | — |
| GET | `/executions` | page, limit, agent_id, status, ticket_id, search |
| GET | `/executions/{execution_id}` | — |
| GET | `/executions/{execution_id}/timeline` | — |

---

### KNOWLEDGE `/api/admin/knowledge`

| Method | Route | Query Params | Body |
|---|---|---|---|
| GET | `/documents` | page, limit, type, status, search | — |
| GET | `/statistics` | — | — |
| GET | `/documents/{document_id}` | — | — |
| GET | `/documents/{document_id}/chunks` | — | — |
| POST | `/upload` | — | `{title, content, type}` |
| DELETE | `/documents/{document_id}` | — | — |
| POST | `/search` | — | `{query, k}` |

---

### ANALYTICS `/api/admin/analytics`

| Method | Route |
|---|---|
| GET | `/overview` |
| GET | `/tickets` |
| GET | `/customers` |
| GET | `/agents` |
| GET | `/knowledge` |

---

### ACTIVITY `/api/admin/activity`

| Method | Route | Query Params |
|---|---|---|
| GET | `` | page, limit, type, level, search |
| GET | `/search` | q, limit |
| GET | `/{activity_id}` | — |

---

### EMAIL `/api/admin/email`

| Method | Route | Query Params | Body |
|---|---|---|---|
| GET | `` | page, limit, status, search | — |
| GET | `/search` | q, limit | — |
| GET | `/{email_id}` | — | — |
| POST | `/reply` | — | `{to, subject, body}` |
| POST | `/{email_id}/retry` | — | — |

---

## ADMIN PAGE → API → DATABASE MAPPING

| Admin Page | API Calls | Tables Queried |
|---|---|---|
| `/admin` (dashboard) | `GET /analytics/overview`, `GET /observatory/agents`, `GET /activity` | tickets, customers, conversations, execution_steps, knowledge_documents, activity_logs |
| `/admin/tickets` | `GET /tickets`, `GET /tickets/{id}` | tickets JOIN conversations JOIN customers, messages |
| `/admin/conversations` | `GET /conversations`, `GET /conversations/{id}`, `/messages` | conversations JOIN customers, messages |
| `/admin/customers` | `GET /customers`, `GET /customers/{id}`, `/{id}/tickets`, `/{id}/conversations` | customers, tickets, conversations, messages |
| `/admin/ai-observatory` | `GET /observatory/agents`, `GET /observatory/executions`, `GET /observatory/executions/{id}` | execution_steps GROUP, executions, execution_steps |
| `/admin/knowledge` | `GET /knowledge/documents`, `GET /knowledge/statistics`, `POST /search`, `POST /upload`, `DELETE /documents/{id}` | knowledge_documents, ChromaDB |
| `/admin/analytics` | `GET /analytics/overview`, `/tickets`, `/agents` | tickets, customers, conversations, execution_steps, knowledge_documents |
| `/admin/activity` | `GET /activity` | activity_logs |
| `/admin/email` | `GET /email`, `GET /email/{id}`, `POST /reply`, `POST /retry` | email_tickets |
| `/admin/settings` | None — fully static/hardcoded | — |

---

## CUSTOMER 360 — CURRENTLY AVAILABLE DATA

For a given SupportFlow customer ID, here is what can currently be retrieved:

**Identity** ✅
- SupportFlow customer ID (`customers.id`)
- Name (`customers.name`) — may be auto-generated from email
- Email (`customers.email`)
- Tier (`customers.tier`) — always `standard` unless manually set
- Sentiment (`customers.sentiment`) — updated by agent
- Joined date (`customers.joined_date`)
- Last interaction (`customers.last_interaction`)
- company_customer_id → bridges to Company DB

**Support Activity** ✅
- All conversations (channel, status, message count, started_at)
- All messages per conversation
- Escalated tickets (subject, priority, status, created_at)
- total_conversations / resolved_conversations (counters)
- risk_score — always 0, never calculated
- lifetime_value — always 0.0, never calculated

**AI Execution** ✅ (via observatory, filterable by conversation)
- execution traces per conversation
- per-agent step records (agent name, status, approximate latency)
- intent, confidence, sentiment per execution
- escalated flag

**Company Data** ✅ (via `company_data_agent` during chat, NOT via admin API)
- Orders, order items
- Payments
- Shipments
- Subscriptions
- Addresses
- Business tier (Gold/VIP/etc.)

**What is NOT currently available via any Admin API:**
- No admin endpoint to fetch company data (orders/payments/shipments) for a given customer — company data is only accessible to agents during chat
- `risk_score` always 0
- `lifetime_value` always 0.0
- `interaction_frequency` never populated
- Phone number (not stored in SupportFlow DB — only in company DB)
- `avg_response_time` never calculated
- No per-conversation execution link visible from conversations API (executions are not returned alongside conversations)

---

## MISSING DATA

1. **`customers.risk_score`** — stored as 0, never computed. No logic exists to calculate it.
2. **`customers.lifetime_value`** — stored as 0.0, never populated from company DB total_spent.
3. **`customers.interaction_frequency`** — stored as NULL, never populated.
4. **`customers.avg_response_time`** — stored as 0.0, never calculated.
5. **`customers.tags`** — comma-separated string; never written by any system process, only possible via a missing admin write endpoint.
6. **`execution_steps.cost`** — always 0.0, no token cost tracking implemented.
7. **`execution_steps.latency`** — approximated (`total_duration / step_count`), not real per-agent timing.
8. **`execution_steps.started_at` / `completed_at`** — all steps written at same timestamp post-hoc. Per-step timestamps are fabricated.
9. **`conversations.subject`** — always NULL. Never set on creation.
10. **`email_tickets.ticket_id`** column referenced in `EmailDetailResponse` schema but the column **does not exist in the DB schema**. The `linked_ticket` field is always `None`.
11. **`email_tickets.conversation_id`** exists but `EmailDetailResponse` never surfaces it; the linked conversation is inaccessible from the email admin view.
12. **No `channel` field on `TicketResponse`** — the tickets schema doesn't directly surface `channel`, requiring the JOIN to conversations. `TicketDetailResponse.conversation_channel` exists but `TicketResponse` does not — the tickets list page therefore shows `t.channel || 'web'` (defaulting to 'web' not 'chat').
13. **Telegram channel** — referenced in enums and DB but no handler code in this codebase.
14. **No admin API endpoint for company data** — orders, payments, shipments, subscriptions for a customer are only accessible to agents during live chat, never to admin panel.
15. **`escalated` count** in `AnalyticsService.get_ticket_analytics()` hardcodes `escalated: 0` — never queries the actual escalated ticket count.

---

## API GAPS

| Frontend Expects | Backend Returns | Gap |
|---|---|---|
| `tickets[].channel` | Not in `TicketResponse` schema | Missing from ticket list; page falls back to `t.channel \|\| 'web'` (wrong default) |
| `EmailDetailResponse.ticket_id` | Field exists in schema, NOT in DB | Always null |
| `EmailDetailResponse.linked_ticket` | Field exists in schema | Service always returns `None` |
| `customers[].company_customer_id` | Not in `CustomerResponse` schema | Frontend customer card shows `c.company_customer_id \|\| c.id` — company_customer_id is not returned |
| `overview.tickets.escalated` | `TicketAnalyticsService` hardcodes `escalated: 0` | Always zero |
| `ExecutionResponse.ticket_id` | Not a field — observatory uses `conversation_id`, not `ticket_id` | AI observatory page shows `exec.ticket_id \|\| 'N/A'` — always N/