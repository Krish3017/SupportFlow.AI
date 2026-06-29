# SupportFlow AI — Routing Architecture

**Two Separate Applications in One Codebase**

---

## Overview

SupportFlow AI consists of **two completely independent experiences**:

1. **Customer-Facing Chat** (`/chat`)
2. **Internal Admin Panel** (`/admin`)

These are **not integrated**. They serve different users and different purposes.

---

## Route Structure

```
/
├── /                           → Redirects to /chat (customer entry point)
│
├── /chat                       → Customer-facing chatbot
│   └── layout.tsx              → Minimal layout (no sidebar)
│   └── page.tsx                → Chat interface
│
└── /admin                      → Admin Panel (internal operations)
    ├── layout.tsx              → DashboardLayout (sidebar + header)
    ├── page.tsx                → Overview dashboard
    ├── /tickets                → Ticket management
    ├── /conversations          → Multi-channel conversations
    ├── /customers              → Customer directory
    ├── /ai-observatory         → Agent monitoring
    ├── /knowledge              → Knowledge base management
    ├── /analytics              → Performance metrics
    ├── /activity               → System logs
    └── /settings               → Configuration
```

---

## User Journeys

### Customer Journey
```
Customer visits website
        ↓
/ (root) redirects to /chat
        ↓
Customer interacts with AI chatbot
        ↓
Backend multi-agent system processes request
        ↓
Customer receives response
```

**URL:** `https://supportflow.ai/chat`  
**Layout:** Full-screen chat interface (no sidebar)  
**Components:** `ChatContainer`, `MessageList`, `MessageInput`  
**Backend API:** `POST /api/chat` (existing)

---

### Admin Journey
```
Support agent navigates to admin panel
        ↓
/admin → Overview dashboard
        ↓
Agent monitors tickets, customers, AI agents
        ↓
Agent reviews agent execution traces
        ↓
Agent manages knowledge base
```

**URL:** `https://supportflow.ai/admin`  
**Layout:** Sidebar + Header (DashboardLayout)  
**Components:** AgentHealthCard, TicketCard, CustomerCard, etc.  
**Backend API:** `GET /api/tickets`, `GET /api/agents/health`, etc. (to be created in Phase 3)

---

## Key Differences

| Aspect | Customer Chat (`/chat`) | Admin Panel (`/admin`) |
|--------|------------------------|------------------------|
| **Purpose** | Customer support interface | Internal operations monitoring |
| **Users** | Customers (public) | Support agents, managers (authenticated) |
| **Layout** | Minimal, full-screen chat | Sidebar + Header + Main content |
| **Authentication** | None (or optional) | Required (JWT in Phase 3) |
| **API** | Existing chat API | New admin APIs (Phase 3) |
| **Real-time** | Chat messages | Agent executions, logs, tickets |
| **Theme** | Light/Dark toggle | Light/Dark toggle |

---

## File Structure

```
app/
├── layout.tsx                  # Root layout (ThemeProvider)
├── page.tsx                    # Redirects to /chat
│
├── chat/
│   ├── layout.tsx              # Chat-specific metadata
│   └── page.tsx                # ChatContainer component
│
└── admin/
    ├── layout.tsx              # DashboardLayout wrapper
    ├── page.tsx                # Overview dashboard
    ├── tickets/
    │   └── page.tsx
    ├── conversations/
    │   └── page.tsx
    ├── customers/
    │   └── page.tsx
    ├── ai-observatory/
    │   └── page.tsx
    ├── knowledge/
    │   └── page.tsx
    ├── analytics/
    │   └── page.tsx
    ├── activity/
    │   └── page.tsx
    └── settings/
        └── page.tsx
```

---

## Navigation

### Customer Navigation
**None.** Single-page chat interface. No sidebar, no header navigation.

Customers may see:
- Chat input
- Message history
- Theme toggle (optional)

### Admin Navigation

**Sidebar** (fixed left, always visible on desktop):
- Overview
- Conversations (separator)
- Tickets
- Customers (separator)
- AI Observatory
- Knowledge Base (separator)
- Analytics
- Activity (separator)
- Settings

**Header** (top bar):
- Global search (Cmd+K)
- Theme toggle
- Notifications dropdown
- Profile menu

---

## Layouts

### Root Layout (`app/layout.tsx`)
- Applies to ALL routes
- Provides `ThemeProvider` (next-themes)
- Loads fonts (Geist Sans, Geist Mono)
- Sets global CSS

### Chat Layout (`app/chat/layout.tsx`)
- Minimal wrapper
- Sets page metadata
- No sidebar, no header

### Admin Layout (`app/admin/layout.tsx`)
- Wraps with `DashboardLayout`
- Includes `Sidebar` + `Header`
- Sets admin metadata

---

## URL Examples

### Customer URLs
```
/                                → Redirects to /chat
/chat                            → Customer chatbot
```

### Admin URLs
```
/admin                           → Overview dashboard
/admin/tickets                   → Ticket management (table + kanban)
/admin/tickets?status=escalated  → Filtered ticket view
/admin/customers                 → Customer directory
/admin/customers/C001            → Customer detail (Phase 3)
/admin/ai-observatory            → Agent monitoring
/admin/knowledge                 → Knowledge base documents
/admin/analytics                 → Performance charts
/admin/activity                  → System logs
/admin/activity?type=agent       → Filtered agent logs
/admin/settings                  → Configuration tabs
```

---

## Backend API Separation

### Existing Chat API (Already Implemented)
```typescript
POST /api/chat
{
  message: string;
  session_id: string;
  customer_id: string;
}
```

Used by: `/chat` page  
Handled by: FastAPI + LangGraph multi-agent system

---

### New Admin APIs (Phase 3)
```typescript
GET  /api/tickets
GET  /api/tickets/:id
POST /api/tickets
PATCH /api/tickets/:id/status

GET  /api/customers
GET  /api/customers/:id

GET  /api/agents/health
GET  /api/agents/executions
GET  /api/agents/executions/:id

GET  /api/conversations
GET  /api/conversations/:id/messages

GET  /api/knowledge/documents
POST /api/knowledge/documents
DELETE /api/knowledge/documents/:id

GET  /api/activity
GET  /api/activity?type=agent

GET  /api/analytics/metrics
GET  /api/analytics/charts
```

Used by: `/admin/*` pages  
Handled by: New FastAPI endpoints (to be created)

---

## Authentication (Phase 3)

### Customer Chat
- **No auth required** (public access)
- Optional: Session tracking via `session_id`
- Rate limiting by IP

### Admin Panel
- **Auth required**
- JWT token stored in `localStorage`
- Protected routes (middleware in Next.js)
- Roles: Admin, Manager, Agent, Viewer

**Login flow:**
```
User visits /admin
        ↓
Middleware checks JWT
        ↓
If not authenticated → Redirect to /admin/login
        ↓
User enters credentials
        ↓
POST /api/auth/login
        ↓
Receive JWT token
        ↓
Store in localStorage
        ↓
Redirect to /admin
```

---

## Real-Time Updates

### Customer Chat
- **Streaming responses** via Server-Sent Events (SSE)
- Already implemented in `ChatContainer.tsx`
- Endpoint: `POST /api/chat` (streaming)

### Admin Panel
- **Live activity feed** via SSE
- **Agent executions** via WebSocket
- **Ticket updates** via polling (5s interval) or SSE

**SSE Example (Phase 3):**
```typescript
// In /admin page
useEffect(() => {
  const eventSource = new EventSource('/api/activity/stream');
  eventSource.onmessage = (event) => {
    const newLog = JSON.parse(event.data);
    setActivityLog(prev => [newLog, ...prev]);
  };
  return () => eventSource.close();
}, []);
```

---

## Deployment

### Development
```bash
npm run dev
# Customer chat:  http://localhost:3000/chat
# Admin panel:    http://localhost:3000/admin
```

### Production
```bash
npm run build
npm start
```

**Vercel Deployment:**
- Single Next.js app
- Two separate entry points: `/chat` and `/admin`
- No subdomain needed (but optional: `admin.supportflow.ai` → `/admin`)

---

## Mobile Considerations

### Customer Chat
- Full responsive
- Mobile-first design
- Touch-optimized input
- No desktop-only features

### Admin Panel
- Desktop-first (primary use case)
- Responsive down to tablet
- Mobile sidebar collapses (hamburger menu — TODO Phase 3)
- Some tables may require horizontal scroll on mobile

---

## Security

### Customer Chat (`/chat`)
- Public access
- Rate limiting (prevent abuse)
- Input sanitization
- No sensitive data exposed

### Admin Panel (`/admin`)
- **Authentication required**
- RBAC (role-based permissions)
- Audit logs for admin actions
- API keys hidden
- CSRF protection

---

## Migration from Old Structure

### Before (Phase 2 Initial)
```
/               → /dashboard (wrong)
/dashboard      → Admin panel
/dashboard/*    → Admin pages
```

### After (Phase 2 Refactored)
```
/               → /chat (correct)
/chat           → Customer chatbot
/admin          → Admin panel
/admin/*        → Admin pages
```

**Changes Made:**
1. Created `/chat` route with existing `ChatContainer`
2. Moved `/dashboard` → `/admin`
3. Updated all sidebar links (`/dashboard/*` → `/admin/*`)
4. Updated root redirect (`/dashboard` → `/chat`)
5. Added separate layouts for chat vs admin
6. Build passing ✅

---

## Future Enhancements

### Customer Portal (Phase 4+)
Optional customer self-service portal:
```
/portal                     → Customer login
/portal/tickets             → Customer's own tickets
/portal/history             → Conversation history
```

### Public Landing Page (Phase 4+)
Marketing/information page:
```
/                           → Landing page
/about                      → About SupportFlow AI
/pricing                    → Pricing plans
/docs                       → Documentation
```

If landing page added, update root:
```typescript
// app/page.tsx
export default function Home() {
  return <LandingPage />;  // Instead of redirect
}
```

---

## Summary

**Two Apps, One Codebase:**

1. **Customer Chat** (`/chat`) → Public, existing functionality preserved
2. **Admin Panel** (`/admin`) → Internal, new UI from Phase 2

**Clean Separation:**
- Different URLs
- Different layouts
- Different APIs
- Different users
- Different authentication

**No Overlap:**
- Customers never see admin panel
- Admins access admin panel directly (`/admin`)
- Both can coexist without conflict

**Ready for Phase 3:**
- Backend integration
- Authentication
- Real-time features
- Full production deployment

---

**Architecture Refactor Complete ✅**
