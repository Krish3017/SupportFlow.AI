# SupportFlow AI

> A multi-agent customer support system that handles customer queries across multiple channels using specialized AI agents.

Architecture
<img width="1672" height="941" alt="ChatGPT Image Jun 10, 2026, 06_10_11 PM" src="https://github.com/user-attachments/assets/1e5e1eaa-5c86-4d91-9276-53c1489f9df8" />


## What is SupportFlow AI?

Most AI support tools follow a simple workflow:

```text
Customer → LLM → Response
```

SupportFlow AI takes a different approach.

Every customer request is processed by a team of specialized AI agents that collaborate to understand the request, retrieve knowledge, generate responses, and decide whether human intervention is required.

Currently supports:

* Email Support
* Web Chat
* WhatsApp (In Progress)

---

## Workflow Architecture

```text


                    ┌─────────────────────┐
                    │  Email / Chat /     │
                    │  WhatsApp (Planned) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Intent Agent     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Customer Intelligence│
                    │        Agent        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Priority Agent    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Route Decision    │
                    └───────┬─────┬───────┘
                            │     │
                     Simple │     │ Complex
                            │     │
                            ▼     ▼
                   ┌───────────┐ ┌─────────────────┐
                   │Resolution │ │ Knowledge Agent │
                   │  Agent    │ │      (RAG)      │
                   └─────┬─────┘ └────────┬────────┘
                         │                │
                         └───────┬────────┘
                                 │
                                 ▼
                      ┌───────────────────┐
                      │ Resolution Agent  │
                      └─────────┬─────────┘
                                │
                                ▼
                      ┌───────────────────┐
                      │ Escalation Agent  │
                      └───────┬─────┬─────┘
                              │     │
                              │     │
                              ▼     ▼
                      ┌─────────┐ ┌─────────────┐
                      │Resolved │ │ Escalated   │
                      │         │ │ to Human    │
                      └─────────┘ └─────────────┘

```
### Shared Infrastructure

* **Groq (LLaMA 3 70B)** → Powers all agents
* **SQLite** → Customer data, conversations, tickets, and memory
* **ChromaDB** → Vector store used by the Knowledge Agent
* **Gmail API** → Incoming email ingestion
* **Resend** → Outgoing customer and escalation emails
---

## AI Agents

### Intent Agent

* Detects customer intent
* Analyzes sentiment
* Calculates confidence

### Customer Intelligence Agent

* Retrieves customer context
* Reviews interaction history
* Identifies customer tier

### Priority Agent

* Assigns priority levels
* Detects critical situations

### Knowledge Agent

* Retrieves information using RAG
* Searches company knowledge base
* Uses ChromaDB vector search

### Resolution Agent

* Generates personalized responses
* Combines retrieved knowledge and customer context

### Escalation Agent

* Determines if human intervention is required
* Notifies managers when escalation occurs

---

## Features

* Multi-Agent Architecture
* LangGraph Orchestration
* Retrieval-Augmented Generation (RAG)
* Gmail Integration
* Automated Email Responses
* Customer Context Retrieval
* Ticket Prioritization
* Human Escalation Workflows
* SQLite Persistence
* ChromaDB Vector Search

---

## Architecture

### Supported Channels

```text
Email
Chat
WhatsApp (Coming Soon)
        │
        ▼
 SupportFlow AI
```

### Core Technologies

* LangGraph
* LangChain
* FastAPI
* Groq (LLaMA 3 70B)
* ChromaDB
* SQLite
* Gmail API
* Resend
* Next.js

---

## Project Structure

```text
SupportFlowAI/
│
├── backend/
│   ├── agents/
│   ├── routers/
│   ├── services/
│   ├── state/
│   ├── data/
│   ├── chroma_db/
│   └── main.py
│
├── frontend/
│   └── Next.js UI
│
└── README.md
```

---

## Getting Started

### 1. Clone Repository

```bash
git clone <repo-url>
cd SupportFlowAI
```

### 2. Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate
# Windows:
# venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create:

```bash
.env
```

Example:

```env
GROQ_API_KEY=

RESEND_API_KEY=

GMAIL_CREDENTIALS_PATH=

GMAIL_TOKEN_PATH=

MANAGER_EMAIL=

DATABASE_PATH=

CHROMA_DB_PATH=
```

### 4. Run Backend

```bash
uvicorn main:app --reload
```

### 5. Run Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Roadmap

### Completed

* Multi-Agent Workflow
* RAG Pipeline
* Gmail Integration
* Customer Context System
* Priority Detection
* Email Escalation
* Automated Responses

### In Progress

* WhatsApp Integration
* Supervisor Agent

### Planned

* Human-in-the-Loop Approvals
* Business Intelligence Agent
* Unified Support Dashboard
* CRM Integrations

---

## Why This Project?

This project was built to explore how multiple AI agents can collaborate to solve customer support problems more effectively than a single LLM workflow.

The goal is not to build another chatbot.

The goal is to build AI systems that operate more like real teams.

---

## License

MIT License
