# Component Documentation

Complete reference for all chat components.

## Type Definitions

### Message

**File:** `types/chat.ts`

```typescript
export interface Message {
  id: string;           // Unique identifier (e.g., "user-1717200000000")
  role: 'user' | 'assistant';  // Message sender
  content: string;      // Message text
  timestamp: Date;      // When message was sent
}
```

Future extensions:
```typescript
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  
  // Future additions:
  agentType?: 'intent' | 'knowledge' | 'resolution';
  metadata?: {
    confidence?: number;
    sources?: string[];
    tokens?: number;
  };
  status?: 'sending' | 'sent' | 'error';
}
```

## Components

### ChatContainer

**File:** `components/chat/ChatContainer.tsx`

Main container component that manages chat state and orchestrates child components.

**Props:** None (root component)

**State:**
```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [isLoading, setIsLoading] = useState(false);
```

**Key Methods:**
```typescript
const handleSendMessage = async (content: string) => {
  // 1. Create user message
  // 2. Add to state
  // 3. Call API (placeholder for now)
  // 4. Add assistant response
}
```

**Structure:**
```tsx
<Card>
  <Header />
  <MessageList messages={messages} />
  <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
</Card>
```

**Usage:**
```tsx
import { ChatContainer } from '@/components/chat';

export default function Page() {
  return <ChatContainer />;
}
```

---

### MessageList

**File:** `components/chat/MessageList.tsx`

Scrollable container for displaying all messages.

**Props:**
```typescript
interface MessageListProps {
  messages: Message[];  // Array of messages to display
}
```

**Features:**
- Auto-scroll to bottom on new messages
- Empty state when no messages
- Uses shadcn/ui `ScrollArea` component

**Internal State:**
```typescript
const scrollRef = useRef<HTMLDivElement>(null);
```

**Auto-scroll Effect:**
```typescript
useEffect(() => {
  if (scrollRef.current) {
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }
}, [messages]);
```

**Empty State:**
```tsx
<div className="flex h-full items-center justify-center">
  <div className="text-center text-muted-foreground">
    <p className="text-lg font-medium">Welcome to Customer Support</p>
    <p className="text-sm mt-2">How can we help you today?</p>
  </div>
</div>
```

**Usage:**
```tsx
<MessageList messages={messages} />
```

---

### MessageBubble

**File:** `components/chat/MessageBubble.tsx`

Individual message display component.

**Props:**
```typescript
interface MessageBubbleProps {
  message: Message;  // Single message to display
}
```

**Styling:**
- User messages: Right-aligned, primary background
- Assistant messages: Left-aligned, muted background
- Rounded corners, padding
- Timestamp below message

**Layout:**
```tsx
<div className={isUser ? 'justify-end' : 'justify-start'}>
  <div className={isUser ? 'bg-primary' : 'bg-muted'}>
    <p>{message.content}</p>
    <time>{timestamp}</time>
  </div>
</div>
```

**Styling Logic:**
```typescript
const isUser = message.role === 'user';

// Container alignment
className={cn('flex w-full', isUser ? 'justify-end' : 'justify-start')}

// Bubble styling
className={cn(
  'max-w-[80%] rounded-2xl px-4 py-3 text-sm',
  isUser
    ? 'bg-primary text-primary-foreground'
    : 'bg-muted text-foreground'
)}
```

**Usage:**
```tsx
<MessageBubble message={message} />
```

---

### MessageInput

**File:** `components/chat/MessageInput.tsx`

Input field and send button for user messages.

**Props:**
```typescript
interface MessageInputProps {
  onSendMessage: (content: string) => void;  // Callback when message sent
  disabled?: boolean;                         // Disable during loading
}
```

**Internal State:**
```typescript
const [input, setInput] = useState('');  // Current input value
```

**Key Methods:**
```typescript
const handleSend = () => {
  if (input.trim() && !disabled) {
    onSendMessage(input.trim());
    setInput('');  // Clear input after sending
  }
};

const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
};
```

**Features:**
- Enter key to send
- Auto-clear after sending
- Disabled state during loading
- Trim whitespace
- Send button with icon

**Usage:**
```tsx
<MessageInput
  onSendMessage={handleSendMessage}
  disabled={isLoading}
/>
```

---

## shadcn/ui Components Used

### Button

**File:** `components/ui/button.tsx`

Used in `MessageInput` for the send button.

**Props:**
```typescript
size="icon"      // Icon-only button
disabled={...}   // Disable state
onClick={...}    // Click handler
```

### Card

**File:** `components/ui/card.tsx`

Used in `ChatContainer` for the main container.

**Features:**
- Border, shadow, rounded corners
- Semantic structure for content

### Input

**File:** `components/ui/input.tsx`

Used in `MessageInput` for text entry.

**Props:**
```typescript
value={...}              // Controlled value
onChange={...}           // Change handler
onKeyPress={...}         // Enter key detection
placeholder="..."        // Placeholder text
disabled={...}           // Disable state
```

### ScrollArea

**File:** `components/ui/scroll-area.tsx`

Used in `MessageList` for message scrolling.

**Features:**
- Custom scrollbar styling
- Smooth scrolling
- Cross-browser compatibility

---

## Styling Reference

### Theme Colors

Defined in `app/globals.css`:

**Light Mode:**
- `--background`: White
- `--foreground`: Near black
- `--primary`: Dark (for user messages)
- `--muted`: Light gray (for assistant messages)

**Dark Mode:**
- `--background`: Near black
- `--foreground`: Near white
- `--primary`: Light (for user messages)
- `--muted`: Dark gray (for assistant messages)

### Utility Classes

```typescript
cn()  // from lib/utils.ts - combines classnames conditionally
```

Example:
```typescript
cn(
  'base classes',
  condition && 'conditional classes',
  'more base classes'
)
```

---

## State Management

### Current (React State)

```typescript
// Local state in ChatContainer
const [messages, setMessages] = useState<Message[]>([]);
const [isLoading, setIsLoading] = useState(false);
```

### Future (Zustand/Context)

When the app grows, consider:

```typescript
// stores/chat.ts
import create from 'zustand';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  sessionId: null,
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setLoading: (loading) => set({ isLoading: loading }),
}));
```

---

## Event Flow

### Sending a Message

```
1. User types in MessageInput
   └─> input state updates

2. User presses Enter or clicks Send
   └─> handleSend() called
   └─> onSendMessage(content) callback

3. ChatContainer receives callback
   └─> Creates Message object
   └─> Adds to messages state
   └─> Sets isLoading = true

4. API call (placeholder for now)
   └─> Simulates delay
   └─> Creates assistant Message
   └─> Adds to messages state
   └─> Sets isLoading = false

5. MessageList re-renders
   └─> New messages appear
   └─> Auto-scrolls to bottom
```

---

## Accessibility

### Keyboard Navigation

- **Enter**: Send message
- **Tab**: Navigate between input and button
- **Screen readers**: Proper ARIA labels (to be added)

### Future Improvements

```tsx
// Add ARIA labels
<Input
  aria-label="Message input"
  aria-describedby="message-help"
  {...props}
/>

<Button
  aria-label="Send message"
  onClick={handleSend}
>
  <Send className="h-4 w-4" />
</Button>

// Add role for messages
<div role="log" aria-live="polite" aria-atomic="false">
  <MessageList messages={messages} />
</div>
```

---

## Performance Optimization

### Current

- Unique keys for message list items (`message.id`)
- Auto-scroll only on message array changes
- Minimal re-renders

### Future Optimizations

```typescript
// Memoize components
const MessageBubble = memo(({ message }: MessageBubbleProps) => {
  // ...
});

// Virtual scrolling for long conversations
import { useVirtualizer } from '@tanstack/react-virtual';

// Lazy load message history
const { messages, hasMore, loadMore } = useInfiniteMessages();
```

---

## Error Handling

### Current

Basic error handling in placeholder code.

### Future Implementation

```typescript
const handleSendMessage = async (content: string) => {
  try {
    // ... API call
  } catch (error) {
    // Add error message to chat
    const errorMessage: Message = {
      id: `error-${Date.now()}`,
      role: 'assistant',
      content: 'Sorry, something went wrong. Please try again.',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, errorMessage]);
    
    // Log to monitoring service
    console.error('Chat error:', error);
  } finally {
    setIsLoading(false);
  }
};
```

---

## Testing

### Component Tests

```typescript
// MessageBubble.test.tsx
import { render, screen } from '@testing-library/react';
import { MessageBubble } from './MessageBubble';

test('renders user message', () => {
  const message = {
    id: '1',
    role: 'user',
    content: 'Hello',
    timestamp: new Date(),
  };
  
  render(<MessageBubble message={message} />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

### Integration Tests

```typescript
// ChatContainer.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatContainer } from './ChatContainer';

test('sends message on enter', async () => {
  render(<ChatContainer />);
  
  const input = screen.getByPlaceholderText('Type your message...');
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
  
  expect(await screen.findByText('Test message')).toBeInTheDocument();
});
```

---

## Extending Components

### Adding Message Actions

```typescript
// MessageBubble with actions
<div className="message-bubble">
  <p>{message.content}</p>
  <div className="actions">
    <Button size="sm" onClick={onCopy}>Copy</Button>
    <Button size="sm" onClick={onRegenerate}>Regenerate</Button>
  </div>
</div>
```

### Adding Typing Indicator

```typescript
// In MessageList
{isLoading && (
  <div className="typing-indicator">
    <span></span>
    <span></span>
    <span></span>
  </div>
)}
```

### Adding Message Status

```typescript
interface Message {
  // ...
  status?: 'sending' | 'sent' | 'error';
}

// In MessageBubble
{message.status === 'error' && (
  <span className="error-icon">⚠️</span>
)}
```
