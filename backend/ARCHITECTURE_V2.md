# SupportFlow AI — Feature-Based Architecture (Phase 3B)

**Version:** 2.0.0 (Feature-First)  
**Status:** Ticket Module Complete

---

## Why Feature-Based Architecture?

**Problem with layer-first:**
```
routers/
├── chat.py
├── tickets.py
├── customers.py
├── analytics.py
└── (20+ files mixed together)

services/
├── ticket_service.py
├── customer_service.py
└── (20+ files mixed together)
```

**Why this is bad for SupportFlow AI:**
- Features scattered across 4+ folders
- Hard to understand ticket module in isolation
- Shared files grow unwieldy (50+ routes in one router)
- Team conflicts (everyone edits `routers/__init__.py`)
- Unclear ownership

**Solution: Feature modules**
```
apps/
├── tickets/
│   ├── router.py      ← All ticket routes
│   ├── service.py     ← Ticket business logic
│   ├── repository.py  ← Ticket DB operations
│   └── schemas.py     ← Ticket DTOs
└── customers/
    ├── router.py
    ├── service.py
    ├── repository.py
    └── schemas.py
```

**Benefits:**
- ✅ Feature complete in one folder
- ✅ Easy to understand (`apps/tickets/` has everything)
- ✅ No merge conflicts between features
- ✅ Clear ownership (tickets team owns `apps/tickets/`)
- ✅ Can delete entire feature by removing folder

---

## New Structure

```
backend/
├── apps/                      # FEATURE MODULES
│   ├── chat/
│   │   ├── router.py
│   │   └── __init__.py
│   │
│   ├── tickets/               # ✅ COMPLETE (Reference Implementation)
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   │
│   ├── customers/             # Next
│   ├── conversations/         # Next
│   ├── analytics/             # Next
│   ├── knowledge/             # Next
│   ├── activity/              # Next
│   ├── observatory/           # Next
│   └── email/                 # Next
│
├── agents/                    # SHARED - LangGraph agents
│   ├── intent_agent.py
│   ├── customer_intelligence_agent.py
│   ├── priority_agent.py
│   ├── knowledge_agent.py
│   ├── resolution_agent.py
│   ├── escalation_agent.py
│   └── email_agent.py
│
├── core/                      # SHARED - Infrastructure
│   ├── config.py
│   ├── logging_config.py
│   ├── errors.py
│   └── responses.py
│
├── repositories/              # SHARED - Base classes only
│   └── base.py
│
├── utils/                     # SHARED - Generic utilities
│   ├── pagination.py
│   └── filtering.py
│
├── state/                     # SHARED - LangGraph state
│   └── schema.py
│
├── database.py                # SHARED - DB operations
├── database_schema_v2.py      # SHARED - Schema
├── gmail_reader.py            # SHARED - Gmail integration
├── main.py                    # ✅ UPDATED - Registers feature routers
└── requirements.txt
```

---

## Ticket Module (Reference Implementation)

### `apps/tickets/router.py`
- FastAPI endpoints
- Query param validation
- Calls service layer
- Returns standardized responses

**Endpoints:**
- `GET /api/admin/tickets` - List with filters
- `GET /api/admin/tickets/{id}` - Detail with execution trace
- `PATCH /api/admin/tickets/{id}/status` - Update status

### `apps/tickets/service.py`
- Business logic
- Orchestrates repository calls
- Transforms data to DTOs
- Logging

### `apps/tickets/repository.py`
- Extends `BaseRepository`
- All SQL queries
- Error handling
- Database operations

### `apps/tickets/schemas.py`
- Pydantic models
- Request DTOs
- Response DTOs
- Enums

---

## Pattern for Future Modules

**Every module follows same structure:**

```python
# apps/[module]/schemas.py
class [Module]Response(BaseModel):
    ...

# apps/[module]/repository.py
class [Module]Repository(BaseRepository):
    def list_items(self, ...): ...
    def get_item(self, id): ...

# apps/[module]/service.py
class [Module]Service:
    def __init__(self):
        self.repository = [Module]Repository()

    def list_items(self, ...):
        data = self.repository.list_items(...)
        return [self._to_response(d) for d in data]

# apps/[module]/router.py
router = APIRouter(prefix="/api/admin/[module]", tags=["[module]"])

@router.get("")
async def list_items(service: [Module]Service = Depends()):
    result = service.list_items()
    return success(data=result)

# apps/[module]/__init__.py
from .router import router
__all__ = ["router"]

# main.py
from apps.[module] import router as [module]_router
app.include_router([module]_router)
```

---

## Files Moved/Refactored

### Moved
- `routers/chat.py` → `apps/chat/router.py`

### Created
- `apps/tickets/router.py`
- `apps/tickets/service.py`
- `apps/tickets/repository.py`
- `apps/tickets/schemas.py`

### Updated
- `main.py` - Uses new routers, new logging

### Preserved (Unchanged)
- `agents/*` - All agents untouched
- `state/schema.py` - LangGraph state
- `gmail_reader.py` - Gmail integration
- `database.py` - DB functions (minor import update)

---

## Trade-offs

### ✅ Advantages

**1. Feature isolation**
- Ticket changes don't touch customer code
- Easy to onboard new devs ("work on tickets → go to `apps/tickets/`")
- Can delete dead features cleanly

**2. Scalability**
- Add features without bloating existing files
- No 1000-line router files
- Clear boundaries

**3. Team collaboration**
- Fewer merge conflicts
- Clear ownership
- Parallel development

**4. Maintainability**
- Find all ticket code in one place
- Understand feature without jumping folders
- Local reasoning (router → service → repository within one folder)

### ⚠️ Disadvantages

**1. Duplication risk**
- Features might duplicate utilities
- **Mitigation:** Strong `shared/` folder discipline

**2. Shared concerns**
- Cross-cutting features (auth, logging) need coordination
- **Mitigation:** `core/` infrastructure handles this

**3. Learning curve**
- New pattern for team
- **Mitigation:** Ticket module is reference template

**4. Over-modularization risk**
- Tiny features get own folder
- **Mitigation:** Combine related features (e.g., `apps/email/` handles both inbound/outbound)

---

## Guidelines for Future Modules

### When to Create New Module

✅ **Create module when:**
- Feature has ≥2 endpoints
- Feature has business logic
- Feature needs DB access
- Feature will grow

❌ **Don't create module when:**
- Single utility endpoint
- Pure computation (goes in `shared/`)
- Infrastructure concern (goes in `core/`)

### Sharing Code

**Module-specific → stays in module**
```python
# apps/tickets/utils.py
def format_ticket_id(id): ...
```

**Used by 2+ modules → promote to shared**
```python
# shared/formatting.py
def format_id(prefix, id): ...
```

### Database Access

**Module needs custom queries → create repository**
```python
# apps/tickets/repository.py
class TicketRepository(BaseRepository):
    ...
```

**Module uses generic CRUD → use BaseRepository directly**
```python
# apps/simple_module/service.py
from repositories.base import BaseRepository

class SimpleService:
    def __init__(self):
        self.db = BaseRepository()
        
    def get_item(self, id):
        return self.db._execute_query("SELECT * FROM items WHERE id = ?", (id,), fetch_one=True)
```

---

## Next Steps

### Immediate (Phase 3B continued)
1. **Create remaining modules:**
   - `apps/customers/` - Customer management
   - `apps/conversations/` - Conversation history
   - `apps/observatory/` - Agent monitoring
   - `apps/analytics/` - Metrics and charts
   - `apps/knowledge/` - Knowledge base
   - `apps/activity/` - Activity logs

2. **Frontend integration:**
   - Install TanStack Query
   - Connect tickets page to `/api/admin/tickets`
   - Add loading/error states
   - Replace mock data

### Future (Phase 4+)
- `apps/auth/` - Authentication module
- `apps/settings/` - Settings management
- `apps/webhooks/` - Webhook management
- `apps/integrations/` - Third-party integrations

---

## Migration Checklist

### ✅ Completed (Phase 3B)
- [x] Create `apps/` folder structure
- [x] Move chat module
- [x] Implement ticket module (reference)
- [x] Update `main.py` to use feature routers
- [x] Update imports

### 🔄 In Progress
- [ ] Connect frontend tickets page
- [ ] Add execution tracking
- [ ] Populate DB with test data

### ⏳ Pending
- [ ] Create remaining 7 modules
- [ ] SSE endpoints
- [ ] Full frontend integration

---

## Summary

**Architecture Evolution:**

**Phase 3A:** Layer-first (core → repositories → routers)  
**Phase 3B:** Feature-first (`apps/[module]/`)

**Why:** SupportFlow AI will have 10+ major features. Feature-based architecture scales better.

**Reference:** `apps/tickets/` is the template for all future modules.

**Next module:** Copy `apps/tickets/`, rename, adapt. Same structure every time.

---

**Feature-Based Architecture Complete — Ticket Module Operational**
