# Architecture Documentation

## Overview

This document outlines the architecture of the Customer Support Chatbot UI and how it will integrate with the backend multi-agent system.

## Current Implementation (MVP)

### Frontend Architecture

```
┌─────────────────────────────────────────┐
│            app/page.tsx                 │
│         (Main Entry Point)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     components/chat/ChatContainer.tsx   │
│     ┌─────────────────────────────┐     │
│     │  State Management           │     │
│     │  - messages: Message[]      │     │
│     │  - isLoading: boolean       │     │
│     └─────────────────────────────┘     │
└────┬────────────────────────┬───────────┘
     │                        │
     ▼                        ▼
┌────────────────┐    ┌──────────────────┐
│  MessageList   │    │  MessageInput    │
│  - Display     │    │  - User Input    │
│  - Scroll      │    │  - Send Handler  │
└────┬───────────┘    └──────────────────┘
     │
     ▼
┌────────────────┐
│ MessageBubble  │
│ - User/AI      │
│ - Timestamp    │
└────────────────┘
```

### Data Flow (Current)

```
User Types Message
        ↓
MessageInput Component
        ↓
handleSendMessage()
        ↓
Add User Message to State
        ↓
[PLACEHOLDER: Simulate API Delay]
        ↓
Add Assistant Response to State
        ↓
MessageList Updates
        ↓
Auto-scroll to Bottom
```

## Future Architecture (With Backend)

### Full System Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Frontend (React)                  │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │         ChatContainer.tsx                  │    │
│  │                                            │    │
│  │  handleSendMessage() {                    │    │
│  │    // API call will replace placeholder   │    │
│  │    await fetch('/api/chat', {...})        │    │
│  │  }                                         │    │
│  └────────────────┬───────────────────────────┘    │
└───────────────────┼──────────────────────────────────┘
                    │ HTTP/WebSocket
                    ▼
┌──────────────────────────────────────────────────────┐
│              FastAPI Backend                         │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  POST /api/chat                            │    │
│  │  ├─ Session Management                     │    │
│  │  ├─ Message Validation                     │    │
│  │  └─ LangGraph Orchestration                │    │
│  └────────────────┬───────────────────────────┘    │
└───────────────────┼──────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│           LangGraph Multi-Agent System               │
│                                                      │
│  ┌──────────────┐   ┌──────────────┐               │
│  │ Intent Agent │──>│ Router       │               │
│  └──────────────┘   └──────┬───────┘               │
│                            │                        │
│           ┌────────────────┼────────────────┐       │
│           │                │                │       │
│           ▼                ▼                ▼       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │  Knowledge   │ │  Resolution  │ │   Other      ││
│  │    Agent     │ │    Agent     │ │   Agents     ││
│  └──────────────┘ └──────────────┘ └──────────────┘│
│           │                │                │       │
│           └────────────────┼────────────────┘       │
│                            ▼                        │
│                    ┌──────────────┐                 │
│                    │  Synthesizer │                 │
│                    └──────────────┘                 │
└───────────────────────────┬──────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Response   │
                    └──────────────┘
```

## Integration Points

### 1. API Endpoint (Backend - To Be Created)

**File:** `backend/main.py` (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph import Graph

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    session_id: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # 1. Create or retrieve session
    session_id = request.session_id or create_new_session()
    
    # 2. Send message to LangGraph
    graph_response = await langgraph_orchestrator.run(
        message=request.message,
        session_id=session_id
    )
    
    # 3. Return response
    return ChatResponse(
        response=graph_response.text,
        agent_type=graph_response.agent,
        session_id=session_id
    )
```

### 2. Frontend API Client (To Be Created)

**File:** `lib/api.ts`

```typescript
export async function sendMessage(
  message: string,
  sessionId?: string
): Promise<{ response: string; agentType: string; sessionId: string }> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
}
```

### 3. Updated ChatContainer

**File:** `components/chat/ChatContainer.tsx` (Lines 25-45)

**Current (Placeholder):**
```typescript
setTimeout(() => {
  const assistantMessage: Message = {
    id: `assistant-${Date.now()}`,
    role: 'assistant',
    content: 'This is a placeholder response...',
    timestamp: new Date(),
  };
  setMessages((prev) => [...prev, assistantMessage]);
  setIsLoading(false);
}, 1000);
```

**Future (Real Implementation):**
```typescript
try {
  // Get or create session ID
  const sessionId = localStorage.getItem('chatSessionId') || undefined;

  // Call backend API
  const response = await sendMessage(content, sessionId);

  // Store session ID
  if (response.sessionId) {
    localStorage.setItem('chatSessionId', response.sessionId);
  }

  // Add assistant response
  const assistantMessage: Message = {
    id: `assistant-${Date.now()}`,
    role: 'assistant',
    content: response.response,
    timestamp: new Date(),
  };

  setMessages((prev) => [...prev, assistantMessage]);
} catch (error) {
  // Handle error
  console.error('Failed to send message:', error);
  // Show error message to user
} finally {
  setIsLoading(false);
}
```

## LangGraph Agent Flow

### Intent Agent
```python
def intent_agent(state):
    """Classifies user intent"""
    message = state["message"]
    
    # Use LLM to classify intent
    intent = llm.classify(message)
    
    return {
        "intent": intent,  # e.g., "question", "complaint", "request"
        "confidence": 0.95,
        "next_agent": route_to_agent(intent)
    }
```

### Knowledge Agent
```python
def knowledge_agent(state):
    """Retrieves information from knowledge base"""
    query = state["message"]
    
    # Vector search in knowledge base
    results = vector_db.search(query, top_k=5)
    
    return {
        "retrieved_docs": results,
        "answer": synthesize_answer(results, query)
    }
```

### Resolution Agent
```python
def resolution_agent(state):
    """Generates final response"""
    context = state["retrieved_docs"]
    message = state["message"]
    
    # Generate response using LLM
    response = llm.generate(
        context=context,
        message=message,
        tone="helpful and professional"
    )
    
    return {"response": response}
```

## Session Management

### Frontend (localStorage)
```typescript
// Store session ID
localStorage.setItem('chatSessionId', sessionId);

// Retrieve session ID
const sessionId = localStorage.getItem('chatSessionId');

// Clear session (logout/reset)
localStorage.removeItem('chatSessionId');
```

### Backend (Redis/Database)
```python
# Store conversation history
await redis.setex(
    f"session:{session_id}",
    3600,  # 1 hour TTL
    json.dumps(conversation_history)
)

# Retrieve conversation history
history = await redis.get(f"session:{session_id}")
```

## Future Enhancements

### 1. Streaming Responses
```typescript
// Frontend: Handle streaming
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  body: JSON.stringify({ message }),
});

const reader = response.body?.getReader();
let partialMessage = '';

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  partialMessage += new TextDecoder().decode(value);
  // Update UI with partial message
}
```

### 2. WebSocket Connection
```typescript
// Real-time bidirectional communication
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle streaming chunks
};
```

### 3. Agent Visibility
```typescript
// Show which agent is responding
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agentType?: 'intent' | 'knowledge' | 'resolution'; // NEW
}
```

### 4. Typing Indicators
```typescript
// Show when agent is "thinking"
const [agentTyping, setAgentTyping] = useState<string | null>(null);

// Display: "Intent Agent is analyzing..."
```

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://...
```

## Testing Strategy

### Frontend
- Unit tests for components
- Integration tests for API calls
- E2E tests with Playwright

### Backend
- Unit tests for each agent
- Integration tests for LangGraph flow
- Load tests for API endpoints

## Deployment

### Frontend (Vercel)
```bash
vercel deploy
```

### Backend (Docker)
```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring

- **Frontend:** Vercel Analytics
- **Backend:** FastAPI metrics endpoint
- **Agents:** LangSmith tracing
- **Errors:** Sentry integration
