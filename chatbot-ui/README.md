# Customer Support Chatbot UI

A minimal, clean chat interface for AI-powered customer support, built with Next.js, React, TypeScript, Tailwind CSS, and shadcn/ui.

## Overview

This is the MVP frontend for a multi-agent customer support system. The UI is intentionally minimal and focused solely on the chat interface.

## Features

- ✅ Clean, centered chat interface
- ✅ Modern ChatGPT-style layout
- ✅ Responsive design
- ✅ Dark mode support
- ✅ Message history with timestamps
- ✅ Auto-scroll to latest message
- ✅ Enter key to send
- ✅ Loading states

## Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Icons:** Lucide React

## Project Structure

```
chatbot-ui/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main page with chat container
│   └── globals.css         # Global styles & theme variables
├── components/
│   ├── chat/
│   │   ├── ChatContainer.tsx    # Main chat component
│   │   ├── MessageList.tsx      # Scrollable message area
│   │   ├── MessageBubble.tsx    # Individual message bubble
│   │   ├── MessageInput.tsx     # Input field + send button
│   │   └── index.ts            # Component exports
│   └── ui/                     # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       └── scroll-area.tsx
├── types/
│   └── chat.ts             # Message type definitions
└── lib/
    └── utils.ts            # Utility functions
```

## Component Architecture

### ChatContainer
- **Purpose:** Main chat component managing state
- **State:** Messages array, loading state
- **Future:** Will handle API calls to backend

### MessageList
- **Purpose:** Displays message history
- **Features:** Auto-scroll, empty state
- **Future:** Will handle streaming responses

### MessageBubble
- **Purpose:** Renders individual messages
- **Features:** User/assistant styling, timestamps
- **Future:** Will support markdown, code blocks

### MessageInput
- **Purpose:** Text input and send button
- **Features:** Enter key support, disabled state
- **Future:** Will add file upload, voice input

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## Future Integration Points

### 1. API Integration (ChatContainer.tsx:25)

Replace the placeholder response logic with actual API calls:

```typescript
// Current placeholder code at line 25-45
// Will be replaced with:

const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: content, sessionId }),
});

const data = await response.json();
```

### 2. Backend Connection

**FastAPI Backend** (to be created)
- Endpoint: `POST /api/chat`
- Request: `{ message: string, sessionId?: string }`
- Response: `{ response: string, agentType: string }`

### 3. Multi-Agent System Integration

The backend will orchestrate these agents using **LangGraph**:

1. **Intent Agent**
   - Classifies user query
   - Routes to appropriate agent
   - Returns: `{ intent: string, confidence: number }`

2. **Knowledge Agent**
   - Retrieves relevant information
   - Searches knowledge base
   - Returns: `{ answer: string, sources: [] }`

3. **Resolution Agent**
   - Generates final response
   - Combines knowledge + context
   - Returns: `{ response: string }`

### 4. Streaming Support

For real-time responses, add streaming:

```typescript
const reader = response.body?.getReader();
// Stream chunks and update UI progressively
```

### 5. Session Management

Add session persistence:
- Store `sessionId` in localStorage
- Send with each request
- Backend maintains conversation history

### 6. Enhanced Features (Post-MVP)

- **Message Actions:** Copy, regenerate
- **Typing Indicators:** Show when agent is responding
- **Error Handling:** Retry logic, error messages
- **File Upload:** Support attachments
- **Voice Input:** Speech-to-text
- **Markdown:** Rich text in responses
- **Code Blocks:** Syntax highlighting

## What This Project Does NOT Include

By design, this MVP excludes:
- ❌ Sidebar navigation
- ❌ Dashboard
- ❌ Analytics pages
- ❌ Settings pages
- ❌ Authentication
- ❌ Multiple routes
- ❌ User management

These will be added in future iterations as needed.

## Dark Mode

Dark mode is automatically supported via Tailwind CSS and shadcn/ui theme variables. The system respects the user's OS preferences by default.

To add a manual toggle (future):
```typescript
// Add theme provider and toggle button
import { ThemeProvider } from 'next-themes'
```

## Styling Philosophy

The UI follows these principles:
- **Minimal:** Only essential elements
- **Clean:** Generous whitespace
- **Modern:** Rounded corners, smooth animations
- **Professional:** Neutral colors, clear hierarchy
- **Accessible:** Proper contrast, keyboard navigation

Inspired by: ChatGPT + Intercom

## Development Notes

### Type Safety
All components use TypeScript with proper interfaces. See `types/chat.ts` for shared types.

### Component Reusability
Components are intentionally small and focused. Easy to modify or replace.

### Performance
- Auto-scroll only triggers on new messages
- Input is debounced for API calls (future)
- Messages use unique IDs for React keys

### Code Comments
Key integration points are marked with `// TODO:` comments showing where backend logic will be added.

## License

MIT
