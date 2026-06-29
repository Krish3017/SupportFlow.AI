# SupportFlow AI — Backend Architecture (Phase 3A)

**Status:** Foundation Complete  
**Version:** 1.0.0 (Refactored)

---

## Overview

Phase 3A introduces clean layered architecture to SupportFlow AI backend, preparing for scalable admin panel integration while preserving existing chat functionality.

**Goals:**
- ✅ Clean separation of concerns
- ✅ Consistent error handling
- ✅ Centralized logging
- ✅ Type-safe DTOs
- ✅ Reusable utilities
- ✅ Repository pattern for DB access
- ✅ No breaking changes to existing chat API

---

## Project Structure

```
backend/
├── core/                       # NEW - Shared infrastructure
│   ├── __init__.py            # Core exports
│   ├── config.py              # Centralized settings (pydantic-settings)
│   ├── logging_config.py      # Colored logging with emojis
│   ├── errors.py              # Custom exceptions
│   └── responses.py           # Standard API response models
│
├── models/                     # NEW - Pydantic schemas
│   ├── dto.py                 # Request/response DTOs
│   └── domain.py              # (Future) Domain models
│
├── repositories/               # NEW - Data access layer
│   ├── __init__.py
│   ├── base.py                # BaseRepository with common operations
│   └── (future: ticket.py, customer.py, execution.py)
│
├── services/                   # Business logic
│   └── email_service.py       # EXISTING - kept as-is
│
├── routers/                    # API controllers
│   ├── __init__.py
│   ├── chat.py                # EXISTING - will refactor to use new infra
│   └── (future: admin routers)
│
├── agents/                     # UNCHANGED - LangGraph agents
│   ├── __init__.py
│   ├── intent_agent.py
│   ├── customer_intelligence_agent.py
│   ├── priority_agent.py
│   ├── knowledge_agent.py
│   ├── resolution_agent.py
│   ├── escalation_agent.py
│   └── email_agent.py
│
├── state/                      # UNCHANGED - LangGraph state
│   ├── __init__.py
│   └── schema.py
│
├── utils/                      # NEW - Shared utilities
│   ├── __init__.py
│   ├── pagination.py          # PaginationParams, paginate()
│   └── filtering.py           # QueryBuilder, SortOrder
│
├── database.py                 # REFACTORED - uses enhanced schema
├── database_schema_v2.py       # NEW - Enhanced schema with repositories
├── gmail_reader.py             # UNCHANGED
├── ingest.py                   # UNCHANGED
├── main.py                     # WILL REFACTOR - use new logging/config
└── requirements.txt            # Updated with pydantic-settings
```

---

## Layer Responsibilities

### 1. Core (`core/`)

**Infrastructure shared across entire application.**

#### `config.py`
- Centralized settings using `pydantic-settings`
- Environment variable validation
- Type-safe configuration access
- Example:
  ```python
  from core import settings
  print(settings.DATABASE_PATH)
  ```

#### `logging_config.py`
- Colored console logging with emojis
- Plain file logging
- Standardized format across all components
- Replaces scattered `logging.basicConfig()` calls
- Example:
  ```python
  from core import get_logger
  logger = get_logger(__name__)
  logger.info("Agent execution started")
  ```

#### `errors.py`
- Custom exception hierarchy
- Consistent HTTP status codes
- Error detail serialization
- Types:
  - `NotFoundError` (404)
  - `ValidationError` (422)
  - `DatabaseError` (500)
  - `AgentExecutionError` (500)
  - `ExternalServiceError` (502)

#### `responses.py`
- Standard response wrappers
- `SuccessResponse[T]` - typed success wrapper
- `ErrorDetail` - error response structure
- `PaginatedResponse[T]` - paginated data
- Helper functions: `success()`, `error()`, `paginated()`

---

### 2. Models (`models/`)

**Pydantic schemas for validation and serialization.**

#### `dto.py`
- Request/response DTOs
- Enums (Priority, Status, Sentiment, Channel, etc.)
- Type-safe API contracts
- Examples:
  - `TicketResponse` - ticket API output
  - `CustomerResponse` - customer API output
  - `AgentHealthResponse` - agent monitoring output
  - `PaginationParams` - query parameters

---

### 3. Repositories (`repositories/`)

**Data access layer abstracting SQLite operations.**

#### `base.py`
- `BaseRepository` with common CRUD operations
- Context manager for connections
- Automatic error handling
- Transaction management
- Helper methods: `_execute_query()`, `_count()`, `_exists()`

**Benefits:**
- Testable (can mock repository)
- Consistent error handling
- Separation from business logic
- Single source of truth for DB operations

**Future repositories:**
- `ticket_repository.py`
- `customer_repository.py`
- `execution_repository.py`
- `activity_repository.py`

---

### 4. Routers (`routers/`)

**Thin controllers handling HTTP requests.**

**Responsibilities:**
- Parse request
- Validate input (Pydantic)
- Call service/repository
- Return standardized response

**Anti-patterns to avoid:**
- ❌ Business logic in routers
- ❌ Direct DB queries
- ❌ Complex transformations

**Pattern:**
```python
@router.get("/api/admin/tickets")
async def list_tickets(
    pagination: PaginationParams = Depends(),
    status: Optional[Status] = None
):
    # 1. Call repository
    result = ticket_repo.list_tickets(
        status=status,
        limit=pagination.limit,
        offset=pagination.offset
    )

    # 2. Transform to DTO
    tickets = [TicketResponse(**t) for t in result.items]

    # 3. Return standard response
    return paginated(
        items=tickets,
        total=result.meta.total,
        page=pagination.page,
        limit=pagination.limit
    )
```

---

### 5. Services (`services/`)

**Business logic and orchestration.**

Currently only `email_service.py` (preserved from Phase 2).

Future services will:
- Orchestrate multiple repositories
- Handle complex business rules
- Coordinate agent executions
- Manage transactions

---

### 6. Utilities (`utils/`)

**Reusable helpers for cross-cutting concerns.**

#### `pagination.py`
- `PaginationParams` - query param model
- `paginate()` - create paginated response
- Configurable defaults via `settings`

#### `filtering.py`
- `QueryBuilder` - dynamic SQL builder
- `SortOrder` enum
- Safe SQL identifier sanitization

---

## Request Flow

### Admin API Request (Future)

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP GET /api/admin/tickets?status=new&page=1
       ▼
┌─────────────────────────────────────┐
│  Router (routers/admin_tickets.py)  │
│  - Parse query params               │
│  - Validate with Pydantic           │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Repository (ticket_repository.py)  │
│  - Build SQL query                  │
│  - Execute via BaseRepository       │
│  - Return raw dicts                 │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Router (transform to DTOs)         │
│  - Map to TicketResponse            │
│  - Wrap in paginated()              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Client    │
│   (JSON)    │
└─────────────┘
```

### Chat API Request (Existing - Preserved)

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/chat (streaming)
       ▼
┌─────────────────────────────────────┐
│  Router (routers/chat.py)           │
│  - Invoke LangGraph workflow        │
│  - Stream response                  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  LangGraph Workflow                 │
│  Intent → Customer Intelligence →   │
│  Priority → Knowledge → Resolution  │
│  → Escalation                       │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Client    │
│ (SSE stream)│
└─────────────┘
```

---

## Error Handling Strategy

### 1. Exception Hierarchy

```
Exception
└── SupportFlowException (base)
    ├── NotFoundError (404)
    ├── ValidationError (422)
    ├── UnauthorizedError (401)
    ├── ForbiddenError (403)
    ├── ConflictError (409)
    ├── RateLimitError (429)
    ├── DatabaseError (500)
    ├── ExternalServiceError (502)
    └── AgentExecutionError (500)
```

### 2. Usage Pattern

```python
# In repository
if not ticket:
    raise NotFoundError(resource="Ticket", identifier=ticket_id)

# In router (automatic conversion)
@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    try:
        ticket = ticket_repo.get(ticket_id)
        return success(data=TicketResponse(**ticket))
    except SupportFlowException as e:
        raise to_http_exception(e)
```

### 3. Global Exception Handler (Future)

Add to `main.py`:
```python
@app.exception_handler(SupportFlowException)
async def handle_supportflow_exception(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "details": exc.details
        }
    )
```

---

## Logging Strategy

### 1. Standardized Format

**Console (colored):**
```
14:32:15 ℹ️ INFO     [routers.chat] 🚀 NEW REQUEST: Where is my order?
14:32:16 ℹ️ INFO     [agents.intent] 🎯 INTENT AGENT CALLED
14:32:17 ✅ INFO     [agents.intent] Intent detected: order_status
```

**File (plain):**
```
2026-06-28 14:32:15 INFO     [routers.chat] 🚀 NEW REQUEST: Where is my order?
2026-06-28 14:32:16 INFO     [agents.intent] 🎯 INTENT AGENT CALLED
2026-06-28 14:32:17 INFO     [agents.intent] Intent detected: order_status
```

### 2. Usage

```python
from core import get_logger

logger = get_logger(__name__)

logger.info("Operation started")
logger.warning("Potential issue detected")
logger.error("Operation failed", exc_info=True)
```

### 3. Logger Naming

- Routers: `routers.chat`, `routers.admin_tickets`
- Agents: `agents.intent`, `agents.resolution`
- Services: `services.email`
- Repositories: `repositories.ticket`

---

## Database Strategy

### 1. Schema Management

**Current:** SQLite with manual `CREATE TABLE IF NOT EXISTS`

**Phase 3A:**
- Enhanced schema in `database_schema_v2.py`
- Backward compatible (preserves existing tables)
- New tables: `tickets`, `customers`, `agent_executions`, `activity_logs`, `knowledge_documents`, `messages`

**Future (Phase 4):**
- Consider Alembic for migrations
- PostgreSQL for production

### 2. Access Pattern

**Old (Phase 1/2):**
```python
# Direct SQL in router
conn = sqlite3.connect("supportflow.db")
tickets = conn.execute("SELECT * FROM tickets").fetchall()
```

**New (Phase 3A):**
```python
# Repository pattern
class TicketRepository(BaseRepository):
    def list_tickets(self, status=None, limit=50, offset=0):
        query = QueryBuilder("SELECT * FROM tickets")
        query.add_filter("status", status)
        query.add_pagination(limit, offset)
        sql, params = query.build()
        return self._execute_query(sql, params, fetch_all=True)

# Usage
repo = TicketRepository()
tickets = repo.list_tickets(status="new")
```

---

## Pagination & Filtering

### Pagination

**Query params:**
```
GET /api/admin/tickets?page=2&limit=25
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 123,
    "page": 2,
    "limit": 25,
    "pages": 5
  }
}
```

**Implementation:**
```python
from utils import PaginationParams, paginate

pagination = PaginationParams(page=2, limit=25)
# pagination.offset = 25 (auto-calculated)
```

### Filtering

**Dynamic query building:**
```python
from utils import QueryBuilder, SortOrder

builder = QueryBuilder("SELECT * FROM tickets")
builder.add_filter("status", "new")
builder.add_filter("priority", "high")
builder.add_like_filter("subject", "refund")
builder.add_sort("created_at", SortOrder.DESC)
builder.add_pagination(limit=50, offset=0)

query, params = builder.build()
# query = "SELECT * FROM tickets WHERE status = ? AND priority = ? AND subject LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
# params = ["new", "high", "%refund%", 50, 0]
```

---

## Configuration Management

### Environment Variables

**Required:**
- `GROQ_API_KEY` - Groq LLM API key
- `RESEND_API_KEY` - Resend email API key

**Optional (with defaults):**
- `DATABASE_PATH` - SQLite path (default: `supportflow.db`)
- `LLM_MODEL` - Model name (default: `llama-3.3-70b-versatile`)
- `LLM_TEMPERATURE` - Temperature (default: `0`)
- `CORS_ORIGINS` - Allowed origins (default: `http://localhost:3000`)
- `HOST` - Server host (default: `0.0.0.0`)
- `PORT` - Server port (default: `8000`)
- `LOG_LEVEL` - Logging level (default: `info`)

### Usage

```python
from core import settings

# Type-safe access
db_path = settings.DATABASE_PATH
api_key = settings.GROQ_API_KEY

# Validation on startup
# Raises ValueError if required vars missing
```

---

## Preparing for SSE (Not Implemented Yet)

### Architecture Plan

**Endpoint:**
```python
@router.get("/api/admin/stream/activity")
async def stream_activity(request: Request):
    async def event_generator():
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break

            # Fetch new activity
            logs = get_recent_activity()
            for log in logs:
                yield f"data: {json.dumps(log)}\n\n"

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Frontend:**
```typescript
const eventSource = new EventSource('/api/admin/stream/activity');
eventSource.onmessage = (event) => {
  const log = JSON.parse(event.data);
  setActivityLog(prev => [log, ...prev]);
};
```

**Streams to implement (Phase 3B):**
1. `/api/admin/stream/activity` - Live activity logs
2. `/api/admin/stream/tickets` - Ticket updates
3. `/api/admin/stream/executions` - Agent execution traces

---

## Migration Path

### Phase 1 → Phase 3A

**Chat API (Preserved):**
- ✅ No breaking changes
- ✅ Existing `/api/chat` endpoint works
- ✅ Streaming intact
- ✅ LangGraph workflow unchanged

**Gradual Refactoring:**
1. ✅ New infrastructure in `core/`, `utils/`, `repositories/`
2. 🔄 Refactor `main.py` to use new logging
3. 🔄 Refactor `routers/chat.py` to use new error handling
4. ➡️ Add admin routers using new patterns
5. ➡️ Agents stay unchanged (only add execution tracking)

---

## Benefits of New Architecture

### 1. Maintainability
- Clear layer boundaries
- Easy to locate code (`routers/` vs `repositories/` vs `services/`)
- Consistent patterns across codebase

### 2. Testability
- Repository pattern → easy to mock
- Thin routers → simple unit tests
- Business logic in services → isolated testing

### 3. Consistency
- Every endpoint returns same response format
- Centralized error handling
- Standard logging format

### 4. Scalability
- Easy to add new endpoints (follow router pattern)
- Easy to add new DB operations (extend BaseRepository)
- Reusable utilities for pagination/filtering

### 5. Developer Experience
- Type-safe configuration
- Colored logs with emojis
- Clear error messages
- IDE autocomplete for DTOs

---

## Next Steps (Phase 3B)

1. **Refactor existing code:**
   - Update `main.py` to use new logging
   - Add global exception handler
   - Initialize enhanced database schema

2. **Build admin routers:**
   - Tickets API (GET list, GET detail, PATCH status)
   - Customers API (GET list, GET detail)
   - Agent monitoring API (GET health, GET executions)
   - Conversations API (GET list, GET messages)
   - Knowledge API (GET documents)
   - Analytics API (GET metrics, GET charts)
   - Activity API (GET logs)

3. **Add execution tracking:**
   - Instrument LangGraph nodes
   - Log to `agent_executions` table
   - Track input/output/latency/cost

4. **Implement SSE:**
   - Activity stream
   - Ticket updates stream
   - Execution trace stream

5. **Frontend integration:**
   - Install TanStack Query
   - Replace mock data page-by-page
   - Add loading/error states

---

## File Checklist

### ✅ Created (Phase 3A)
- `core/config.py` - Centralized settings
- `core/logging_config.py` - Colored logging
- `core/errors.py` - Custom exceptions
- `core/responses.py` - Response models
- `models/dto.py` - Request/response DTOs
- `repositories/base.py` - BaseRepository
- `utils/pagination.py` - Pagination utilities
- `utils/filtering.py` - Query building
- `database_schema_v2.py` - Enhanced schema

### 🔄 To Refactor (Phase 3B)
- `main.py` - Use new logging/config/errors
- `routers/chat.py` - Use new response models
- `database.py` - Import enhanced schema

### ➡️ To Create (Phase 3B+)
- `routers/admin_tickets.py`
- `routers/admin_customers.py`
- `routers/admin_agents.py`
- `routers/admin_conversations.py`
- `routers/admin_knowledge.py`
- `routers/admin_analytics.py`
- `routers/admin_activity.py`
- `repositories/ticket_repository.py`
- `repositories/customer_repository.py`
- `repositories/execution_repository.py`

---

## Summary

Phase 3A establishes clean architectural foundation:

**Core infrastructure:** ✅ Config, logging, errors, responses  
**Data layer:** ✅ Repository pattern, base operations  
**Utilities:** ✅ Pagination, filtering, query building  
**Schemas:** ✅ DTOs, response models  

**Next:** Build admin APIs on this foundation (Phase 3B).

**Philosophy:** "Strong foundation first, features second."

---

**Architecture Refactor Complete — Ready for Business Features**
