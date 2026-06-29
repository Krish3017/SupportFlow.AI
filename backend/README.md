# SupportFlow AI - Backend

> **Multi-Agent Customer Support Platform** powered by LangGraph, Groq, and FastAPI

SupportFlow AI is an intelligent customer support system that uses multiple specialized AI agents to automatically process customer inquiries through email and chat interfaces. It features RAG-based knowledge retrieval, automatic priority classification, and intelligent escalation to human agents.

---

## Features

- **Multi-Agent Architecture** - Specialized agents for intent classification, knowledge retrieval, customer intelligence, priority assessment, resolution, and escalation
- **Dual-Channel Support** - Handle inquiries via REST API (chat) and Gmail integration (email tickets)
- **RAG-Powered Knowledge Base** - ChromaDB vector store with semantic search for accurate information retrieval
- **Intelligent Prioritization** - Automatic ticket priority assignment based on intent, sentiment, and customer tier
- **Smart Escalation** - Rule-based escalation system for complex or sensitive issues
- **Gmail Integration** - OAuth-authenticated email polling and automated responses via Resend
- **Session Management** - Conversation history tracking for context-aware responses
- **Customer Intelligence** - Customer context retrieval for personalized support
- **Streaming Responses** - Server-Sent Events (SSE) for real-time chat responses
- **SQLite Persistence** - Conversation and ticket storage with full audit trail

---

## Architecture Overview

### Agent Workflow

```
Customer Request (Email/Chat)
         ↓
   Intent Agent
   • Classifies intent category
   • Detects sentiment
   • Extracts language & confidence
         ↓
   Customer Intelligence Agent
   • Retrieves customer context
   • Identifies customer tier
         ↓
   Priority Agent
   • Assigns priority level
   • Considers intent, sentiment, tier
         ↓
   Knowledge Agent (conditional)
   • RAG-based semantic search
   • Retrieves relevant documentation
         ↓
   Resolution Agent
   • Generates contextual response
   • Uses chat history for continuity
         ↓
   Escalation Agent
   • Evaluates escalation conditions
   • Routes to human if needed
         ↓
Response Delivery
• Email: Resend API
• Chat: Streaming SSE
```

### Components

- **FastAPI** - High-performance async web framework
- **LangGraph** - Agent orchestration and workflow management
- **Groq** - Ultra-fast LLM inference (Llama 3.3 70B)
- **ChromaDB** - Vector database for semantic search
- **HuggingFace Embeddings** - Sentence transformers for text embeddings
- **SQLite** - Lightweight database for conversations and tickets
- **Gmail API** - OAuth2 email integration
- **Resend** - Transactional email delivery
- **LangChain** - LLM orchestration utilities

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | FastAPI 0.115.0 |
| **LLM Provider** | Groq (Llama 3.3 70B) |
| **Agent Orchestration** | LangGraph 0.2.45 |
| **Vector Store** | ChromaDB + HuggingFace |
| **Email** | Gmail API + Resend |
| **Database** | SQLite3 |
| **Language** | Python 3.10+ |

---

## Project Structure

```
backend/
├── main.py                          # FastAPI application entry point
├── database.py                      # SQLite connection and queries
├── gmail_reader.py                  # Gmail OAuth and email parsing
├── ingest.py                        # Knowledge base ingestion script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
│
├── agents/                          # Multi-agent system
│   ├── __init__.py
│   ├── intent_agent.py              # Intent classification + sentiment analysis
│   ├── customer_intelligence_agent.py  # Customer context retrieval
│   ├── priority_agent.py            # Priority assignment logic
│   ├── knowledge_agent.py           # RAG-based knowledge retrieval
│   ├── resolution_agent.py          # Response generation
│   ├── escalation_agent.py          # Escalation decision logic
│   └── email_agent.py               # Background email polling + workflow
│
├── routers/                         # API route handlers
│   ├── __init__.py
│   └── chat.py                      # Chat endpoint + LangGraph workflow
│
├── services/                        # External service integrations
│   ├── __init__.py
│   └── email_service.py             # Resend email sending
│
├── state/                           # State management
│   ├── __init__.py
│   └── schema.py                    # LangGraph state schema
│
└── data/                            # Knowledge base files
    └── company_knowledge.txt        # Company policies and information
```

---

## Setup Instructions

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Groq API Key** - [Sign up here](https://console.groq.com/keys)
- **Resend API Key** - [Sign up here](https://resend.com/api-keys)
- **Gmail OAuth Credentials** (optional, for email integration)
  - Create project in [Google Cloud Console](https://console.cloud.google.com/)
  - Enable Gmail API
  - Create OAuth 2.0 credentials
  - Download `credentials.json`

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate (Windows)
   venv\Scripts\activate
   
   # Activate (Mac/Linux)
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   RESEND_API_KEY=your_resend_api_key_here
   SUPPORT_EMAIL=support@yourdomain.com
   MANAGER_EMAIL=manager@yourdomain.com
   ```

5. **Ingest knowledge base**
   ```bash
   python ingest.py
   ```
   This creates the ChromaDB vector store from `data/company_knowledge.txt`

6. **Initialize database**
   The database is auto-created on first run. Tables are created automatically.

7. **(Optional) Setup Gmail OAuth**
   
   If using email integration:
   - Place `credentials.json` in the backend directory
   - Run the Gmail reader once to authorize:
     ```bash
     python gmail_reader.py
     ```
   - A browser window will open for authorization
   - `token.json` will be saved for future use

---

## Running the Application

### Development Mode

```bash
python main.py
```

Server starts at: `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Custom Configuration

```bash
HOST=127.0.0.1 PORT=5000 python main.py
```

---

## API Endpoints

### Health Check

```http
GET /
```

**Response:**
```json
{
  "status": "online",
  "service": "SupportFlow AI",
  "version": "1.0.0"
}
```

---

### Health Status

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "groq_api_configured": true,
  "resend_api_configured": true,
  "endpoints": {
    "chat": "/api/chat"
  }
}
```

---

### Chat (Streaming)

```http
POST /api/chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Where is my order #12345?",
  "customer_id": "cust_123",
  "session_id": "optional_session_id"
}
```

**Response:** `text/event-stream` (Server-Sent Events)

```
data: {"content": "I'll"}
data: {"content": " help"}
data: {"content": " you"}
data: {"content": " track"}
data: {"content": " your"}
data: {"content": " order..."}
data: {"done": true, "session_id": "abc-123"}
```

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM inference | `gsk_xxxxx` |
| `RESEND_API_KEY` | Resend API key for email sending | `re_xxxxx` |

### Email Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPPORT_EMAIL` | Support inbox email | `support@yourdomain.com` |
| `MANAGER_EMAIL` | Escalation recipient email | `manager@yourdomain.com` |
| `FROM_EMAIL` | Sender email for replies | `onboarding@resend.dev` |
| `GMAIL_CREDENTIALS_PATH` | Gmail OAuth credentials file | `credentials.json` |
| `GMAIL_TOKEN_PATH` | Gmail OAuth token file | `token.json` |
| `EMAIL_POLL_INTERVAL_MINUTES` | Email check frequency | `2` |

### Database & Storage

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PATH` | SQLite database file | `supportflow.db` |
| `CHROMA_DB_PATH` | ChromaDB directory | `chroma_db` |
| `KNOWLEDGE_FILE_PATH` | Knowledge base text file | `data/company_knowledge.txt` |
| `EMBEDDING_MODEL` | HuggingFace embedding model | `all-MiniLM-L6-v2` |

### LLM Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_MODEL` | Groq model name | `llama-3.3-70b-versatile` |
| `LLM_TEMPERATURE` | Sampling temperature | `0` |

### Server Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `RELOAD` | Auto-reload on changes | `True` |
| `LOG_LEVEL` | Logging level | `info` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000` |

---

## Testing

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a refund for order #12345"}'
```

### Test with Python

```python
import requests
import json

url = "http://localhost:8000/api/chat"
data = {
    "message": "Where is my order?",
    "customer_id": "cust_123"
}

response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            event = json.loads(line[6:])
            if 'content' in event:
                print(event['content'], end='', flush=True)
            elif event.get('done'):
                print(f"\n[Session ID: {event.get('session_id')}]")
```

---

## Intent Categories

The Intent Agent classifies customer messages into these categories:

| Intent | Description |
|--------|-------------|
| `order_status` | Order tracking inquiries |
| `refund_request` | Refund and return requests |
| `technical_issue` | Technical problems with products/services |
| `product_question` | Product features and specifications |
| `billing_issue` | Payment and billing problems |
| `complaint` | Customer complaints and dissatisfaction |
| `feature_request` | Feature suggestions |
| `account_issue` | Account access and settings |
| `general_inquiry` | General questions |

---

## Email Workflow

The Email Agent runs as a background task and:

1. **Polls Gmail inbox** every N minutes (configurable)
2. **Checks for new emails** in the support label
3. **Saves to database** to prevent duplicate processing
4. **Runs multi-agent workflow** to classify and resolve
5. **Sends response** via Resend:
   - **AI Resolution** - Direct answer to customer
   - **Escalation** - Notification to customer + alert to manager

### Email Templates

- **Resolution Email** - Clean, branded response with AI-generated answer
- **Escalation Email** (Customer) - Notification that a human will assist
- **Escalation Email** (Manager) - Full ticket details with metadata

---

## Database Schema

### `conversations` Table

Stores all chat interactions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `customer_message` | TEXT | Original customer message |
| `intent` | TEXT | Classified intent |
| `sub_intent` | TEXT | Specific sub-category |
| `sentiment` | TEXT | Positive/negative/neutral |
| `confidence` | REAL | Classification confidence (0-1) |
| `final_response` | TEXT | AI-generated response |
| `escalated` | BOOLEAN | Whether escalated to human |
| `priority` | TEXT | Low/medium/high/urgent |
| `timestamp` | TEXT | ISO 8601 timestamp |

### `email_tickets` Table

Stores all email support tickets.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (ticket ID) |
| `gmail_message_id` | TEXT | Gmail message ID (unique) |
| `sender_email` | TEXT | Customer email address |
| `subject` | TEXT | Email subject |
| `body` | TEXT | Email body text |
| `status` | TEXT | pending/resolved/escalated/error |
| `ai_response` | TEXT | Generated AI response |
| `created_at` | TEXT | ISO 8601 timestamp |

---

## Development

### Project Conventions

- **Agents are stateless** - All state is in `AgentState` schema
- **No side effects in agents** - Return state updates only
- **Database writes happen after workflow completes** - Not during agent execution
- **Environment variables for all configuration** - No hardcoded values

### Adding a New Agent

1. Create agent file in `agents/`
2. Define async function accepting `AgentState`
3. Return dict with state updates
4. Add node to graph in `routers/chat.py`
5. Add edge or conditional routing

### Extending the Knowledge Base

Edit `data/company_knowledge.txt` and re-run:

```bash
python ingest.py
```

---

## Troubleshooting

### "GROQ_API_KEY environment variable is required"

- Create `.env` file from `.env.example`
- Add your Groq API key

### "RESEND_API_KEY environment variable is required"

- Sign up at [resend.com](https://resend.com)
- Add API key to `.env`

### Gmail Authentication Fails

- Ensure `credentials.json` is in backend directory
- Check that Gmail API is enabled in Google Cloud Console
- Delete `token.json` and re-authorize if scopes changed

### ChromaDB Not Found

- Run `python ingest.py` to create vector store
- Check that `data/company_knowledge.txt` exists

### CORS Errors

- Add your frontend URL to `CORS_ORIGINS` in `.env`
- Separate multiple origins with commas

### Streaming Not Working

- Ensure client properly handles `text/event-stream`
- Check that `Cache-Control: no-cache` header is set

---

## Future Improvements

- [ ] Add authentication and API key management
- [ ] Implement rate limiting
- [ ] Add Slack integration
- [ ] Support multiple languages
- [ ] Add analytics dashboard
- [ ] Implement A/B testing for responses
- [ ] Add voice channel support
- [ ] Integrate with CRM systems
- [ ] Add sentiment trend analysis
- [ ] Implement automated feedback loop

---

## License

MIT

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## Support

For questions or issues, please open an issue on GitHub.
