-- ==============================================================================
-- SupportFlow AI — Supabase PostgreSQL Schema Script (Phase 1B)
-- Target: Supabase PostgreSQL (Postgres 15+)
-- Schemas: supportflow, company
-- Description: Creates schemas, tables, constraints, foreign keys, and indexes
-- ==============================================================================

BEGIN;

-- ------------------------------------------------------------------------------
-- 1. SCHEMAS
-- ------------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS supportflow;
CREATE SCHEMA IF NOT EXISTS company;

-- ------------------------------------------------------------------------------
-- 2. COMPANY SCHEMA TABLES (Dependency Order)
-- ------------------------------------------------------------------------------

-- 2.1 company.customers
CREATE TABLE IF NOT EXISTS company.customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    customer_tier TEXT DEFAULT 'Bronze',
    account_status TEXT DEFAULT 'active',
    registration_date TIMESTAMPTZ NOT NULL,
    total_orders INTEGER DEFAULT 0,
    total_spent NUMERIC(12,2) DEFAULT 0.00,
    preferred_channel TEXT DEFAULT 'email',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_company_cust_email ON company.customers(email);
CREATE INDEX IF NOT EXISTS idx_company_cust_tier ON company.customers(customer_tier);

-- 2.2 company.addresses
CREATE TABLE IF NOT EXISTS company.addresses (
    address_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES company.customers(customer_id) ON DELETE CASCADE,
    address_type TEXT DEFAULT 'shipping',
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_company_addr_customer ON company.addresses(customer_id);

-- 2.3 company.products
CREATE TABLE IF NOT EXISTS company.products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    stock_status TEXT DEFAULT 'in_stock',
    active_status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_company_prod_category ON company.products(category);
CREATE INDEX IF NOT EXISTS idx_company_prod_stock ON company.products(stock_status);

-- 2.4 company.orders
CREATE TABLE IF NOT EXISTS company.orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES company.customers(customer_id) ON DELETE CASCADE,
    order_date TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    shipping_address_id TEXT REFERENCES company.addresses(address_id) ON DELETE SET NULL,
    expected_delivery_date TIMESTAMPTZ,
    actual_delivery_date TIMESTAMPTZ,
    tracking_information TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_company_ord_customer ON company.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_company_ord_status ON company.orders(status);
CREATE INDEX IF NOT EXISTS idx_company_ord_date ON company.orders(order_date);

-- 2.5 company.order_items
CREATE TABLE IF NOT EXISTS company.order_items (
    item_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES company.orders(order_id) ON DELETE CASCADE,
    product_id TEXT NOT NULL REFERENCES company.products(product_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(12,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_company_item_order ON company.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_company_item_product ON company.order_items(product_id);

-- 2.6 company.payments
CREATE TABLE IF NOT EXISTS company.payments (
    payment_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES company.orders(order_id) ON DELETE CASCADE,
    customer_id TEXT NOT NULL REFERENCES company.customers(customer_id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    transaction_reference TEXT,
    payment_date TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_company_pay_order ON company.payments(order_id);
CREATE INDEX IF NOT EXISTS idx_company_pay_customer ON company.payments(customer_id);

-- 2.7 company.shipments
CREATE TABLE IF NOT EXISTS company.shipments (
    shipment_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES company.orders(order_id) ON DELETE CASCADE,
    carrier TEXT NOT NULL,
    tracking_number TEXT NOT NULL,
    shipment_status TEXT NOT NULL,
    shipped_at TIMESTAMPTZ,
    estimated_delivery TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_company_ship_order ON company.shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_company_ship_tracking ON company.shipments(tracking_number);

-- 2.8 company.subscriptions
CREATE TABLE IF NOT EXISTS company.subscriptions (
    subscription_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES company.customers(customer_id) ON DELETE CASCADE,
    plan TEXT NOT NULL,
    status TEXT NOT NULL,
    billing_cycle TEXT NOT NULL,
    start_date TIMESTAMPTZ NOT NULL,
    renewal_date TIMESTAMPTZ NOT NULL,
    amount NUMERIC(10,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_company_sub_customer ON company.subscriptions(customer_id);
CREATE INDEX IF NOT EXISTS idx_company_sub_status ON company.subscriptions(status);


-- ------------------------------------------------------------------------------
-- 3. SUPPORTFLOW SCHEMA TABLES (Dependency Order)
-- ------------------------------------------------------------------------------

-- 3.1 supportflow.customers
CREATE TABLE IF NOT EXISTS supportflow.customers (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    company_customer_id TEXT REFERENCES company.customers(customer_id) ON DELETE SET NULL,
    tier TEXT DEFAULT 'standard',
    sentiment TEXT DEFAULT 'neutral',
    total_conversations INTEGER DEFAULT 0,
    resolved_conversations INTEGER DEFAULT 0,
    avg_response_time DOUBLE PRECISION DEFAULT 0.0,
    interaction_frequency TEXT,
    last_interaction TIMESTAMPTZ,
    joined_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    risk_score INTEGER DEFAULT 0,
    lifetime_value NUMERIC(12,2) DEFAULT 0.00,
    tags JSONB
);

CREATE INDEX IF NOT EXISTS idx_sf_cust_email ON supportflow.customers(email);
CREATE INDEX IF NOT EXISTS idx_sf_cust_tier ON supportflow.customers(tier);
CREATE INDEX IF NOT EXISTS idx_sf_cust_company_id ON supportflow.customers(company_customer_id);

-- 3.2 supportflow.customer_sessions
CREATE TABLE IF NOT EXISTS supportflow.customer_sessions (
    session_token TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES supportflow.customers(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sf_sessions_token ON supportflow.customer_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sf_sessions_customer ON supportflow.customer_sessions(customer_id);

-- 3.3 supportflow.contact_channels
CREATE TABLE IF NOT EXISTS supportflow.contact_channels (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    contact_id TEXT NOT NULL REFERENCES supportflow.customers(id) ON DELETE CASCADE,
    channel_type TEXT NOT NULL,
    channel_identifier TEXT NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_contact_channels UNIQUE (channel_type, channel_identifier)
);

CREATE INDEX IF NOT EXISTS idx_sf_channels_contact ON supportflow.contact_channels(contact_id);
CREATE INDEX IF NOT EXISTS idx_sf_channels_lookup ON supportflow.contact_channels(channel_type, channel_identifier);

-- 3.4 supportflow.conversations
CREATE TABLE IF NOT EXISTS supportflow.conversations (
    id TEXT PRIMARY KEY,
    contact_id TEXT NOT NULL REFERENCES supportflow.customers(id) ON DELETE CASCADE,
    channel TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    subject TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    session_token TEXT,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_sf_conv_contact ON supportflow.conversations(contact_id);
CREATE INDEX IF NOT EXISTS idx_sf_conv_status ON supportflow.conversations(status);
CREATE INDEX IF NOT EXISTS idx_sf_conv_channel ON supportflow.conversations(channel);
CREATE INDEX IF NOT EXISTS idx_sf_conv_session ON supportflow.conversations(session_token);
CREATE INDEX IF NOT EXISTS idx_sf_conv_updated ON supportflow.conversations(updated_at DESC);

-- 3.5 supportflow.messages
CREATE TABLE IF NOT EXISTS supportflow.messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES supportflow.conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_id TEXT,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_sf_msg_conversation ON supportflow.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_sf_msg_timestamp ON supportflow.messages(timestamp ASC);
CREATE INDEX IF NOT EXISTS idx_sf_msg_execution ON supportflow.messages(execution_id);

-- 3.6 supportflow.executions
CREATE TABLE IF NOT EXISTS supportflow.executions (
    id TEXT PRIMARY KEY,
    message_id TEXT NOT NULL REFERENCES supportflow.messages(id) ON DELETE CASCADE,
    conversation_id TEXT NOT NULL REFERENCES supportflow.conversations(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'running',
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    total_duration DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    intent TEXT,
    sentiment TEXT,
    priority TEXT,
    escalated BOOLEAN DEFAULT FALSE,
    error TEXT,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_sf_exec_message ON supportflow.executions(message_id);
CREATE INDEX IF NOT EXISTS idx_sf_exec_conversation ON supportflow.executions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_sf_exec_status ON supportflow.executions(status);
CREATE INDEX IF NOT EXISTS idx_sf_exec_started ON supportflow.executions(started_at DESC);

-- 3.7 supportflow.execution_steps
CREATE TABLE IF NOT EXISTS supportflow.execution_steps (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES supportflow.executions(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    sequence_order INTEGER NOT NULL,
    status TEXT NOT NULL,
    input_data TEXT,
    output_data TEXT,
    latency DOUBLE PRECISION,
    cost NUMERIC(10,6) DEFAULT 0.000000,
    error TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sf_exec_steps_execution ON supportflow.execution_steps(execution_id);
CREATE INDEX IF NOT EXISTS idx_sf_exec_steps_agent ON supportflow.execution_steps(agent_id);

-- 3.8 supportflow.tickets
CREATE TABLE IF NOT EXISTS supportflow.tickets (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES supportflow.conversations(id) ON DELETE CASCADE,
    contact_id TEXT NOT NULL REFERENCES supportflow.customers(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'open',
    assignee TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    escalation_reason TEXT,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_sf_tkt_conversation ON supportflow.tickets(conversation_id);
CREATE INDEX IF NOT EXISTS idx_sf_tkt_contact ON supportflow.tickets(contact_id);
CREATE INDEX IF NOT EXISTS idx_sf_tkt_status ON supportflow.tickets(status);
CREATE INDEX IF NOT EXISTS idx_sf_tkt_priority ON supportflow.tickets(priority);

-- 3.9 supportflow.activity_logs
CREATE TABLE IF NOT EXISTS supportflow.activity_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_sf_act_type ON supportflow.activity_logs(type);
CREATE INDEX IF NOT EXISTS idx_sf_act_timestamp ON supportflow.activity_logs(timestamp DESC);

-- 3.10 supportflow.knowledge_documents & supportflow.knowledge_chunks
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS supportflow.knowledge_documents (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    chunks_count INTEGER DEFAULT 0,
    retrieval_count INTEGER DEFAULT 0,
    size_bytes BIGINT DEFAULT 0,
    file_path VARCHAR(1000),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sf_know_doc_status ON supportflow.knowledge_documents(status);
CREATE INDEX IF NOT EXISTS idx_sf_know_doc_type ON supportflow.knowledge_documents(type);

CREATE TABLE IF NOT EXISTS supportflow.knowledge_chunks (
    id VARCHAR(255) PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL REFERENCES supportflow.knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    embedding VECTOR(384) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_doc_chunk_index UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_sf_know_chunk_doc_id ON supportflow.knowledge_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_sf_know_chunk_metadata ON supportflow.knowledge_chunks USING gin (metadata);

CREATE INDEX IF NOT EXISTS idx_sf_know_chunk_embedding_hnsw
ON supportflow.knowledge_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 3.11 supportflow.email_tickets
CREATE TABLE IF NOT EXISTS supportflow.email_tickets (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gmail_message_id TEXT UNIQUE,
    sender_email TEXT,
    subject TEXT,
    body TEXT,
    status TEXT DEFAULT 'pending',
    ai_response TEXT,
    conversation_id TEXT REFERENCES supportflow.conversations(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sf_email_gmail_id ON supportflow.email_tickets(gmail_message_id);
CREATE INDEX IF NOT EXISTS idx_sf_email_status ON supportflow.email_tickets(status);

COMMIT;

-- ==============================================================================
-- 4. VERIFICATION QUERIES (Run these in Supabase SQL Editor to verify setup)
-- ==============================================================================
/*
-- Query 1: Verify schemas exist
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name IN ('supportflow', 'company');

-- Query 2: List all tables created in 'supportflow' schema
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'supportflow' 
ORDER BY table_name;

-- Query 3: List all tables created in 'company' schema
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'company' 
ORDER BY table_name;

-- Query 4: Verify cross-schema foreign key (supportflow.customers -> company.customers)
SELECT
    tc.table_schema, 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name = 'customers' 
  AND tc.table_schema = 'supportflow';
*/
