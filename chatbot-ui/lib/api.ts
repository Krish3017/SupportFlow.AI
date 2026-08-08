/**
 * API client for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatResponse {
  content: string;
  done?: boolean;
  session_id?: string;
  conversation_id?: string;
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ConversationHistory {
  conversation_id: string;
  status: string;
  messages: ConversationMessage[];
}

export interface SessionInfo {
  conversation_id: string | null;
  status: string | null;
}

/**
 * Send a chat message and receive streaming response
 * @param message User's message
 * @param sessionId Session identifier
 * @param customerId Customer identifier
 * @param onChunk Callback for each chunk received
 * @returns Promise that resolves with session_id when stream completes
 */
export async function sendChatMessage(
  message: string,
  sessionId: string,
  customerId: string,
  onChunk: (content: string) => void,
  token?: string
): Promise<{ session_id: string | null; conversation_id: string | null }> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      message,
      session_id: sessionId,
      customer_id: customerId
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';
  let returnedSessionId: string | null = null;
  let returnedConversationId: string | null = null;

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);

          try {
            const parsed: ChatResponse = JSON.parse(data);

            if (parsed.done) {
              if (parsed.session_id) {
                returnedSessionId = parsed.session_id;
              }
              if (parsed.conversation_id) {
                returnedConversationId = parsed.conversation_id;
              }
              return { session_id: returnedSessionId, conversation_id: returnedConversationId };
            }

            if (parsed.content) {
              onChunk(parsed.content);
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', e);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  return { session_id: returnedSessionId, conversation_id: returnedConversationId };
}

/**
 * Health check endpoint
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export async function fetchConversationHistory(conversationId: string, token?: string): Promise<ConversationHistory | null> {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}/api/chat/history/${conversationId}`, { headers });
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

export async function fetchSessionConversation(sessionId: string): Promise<SessionInfo> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/session/${sessionId}`);
    if (!response.ok) return { conversation_id: null, status: null };
    return await response.json();
  } catch {
    return { conversation_id: null, status: null };
  }
}

export interface AuthUser {
  id: string;
  email: string;
  name?: string;
  company_customer_id?: string;
}

export async function registerCustomer(email: string, password: string, name?: string): Promise<{ token: string; user: AuthUser }> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || data.detail || 'Registration failed.');
  }
  return data.data;
}

export async function loginCustomer(email: string, password: string): Promise<{ token: string; user: AuthUser }> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || data.detail || 'Login failed.');
  }
  return data.data;
}

export async function logoutCustomer(token?: string): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  } catch (e) {
    console.error('Logout error:', e);
  }
}

export async function getAuthenticatedCustomer(token: string): Promise<AuthUser | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.data;
  } catch {
    return null;
  }
}
