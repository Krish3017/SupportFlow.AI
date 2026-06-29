/**
 * API client for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatResponse {
  content: string;
  done?: boolean;
  session_id?: string;
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
  onChunk: (content: string) => void
): Promise<string | null> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
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

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || ''; // Keep incomplete message in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); // Remove 'data: ' prefix

          try {
            const parsed: ChatResponse = JSON.parse(data);

            if (parsed.done) {
              // Capture session_id from done signal
              if (parsed.session_id) {
                returnedSessionId = parsed.session_id;
              }
              return returnedSessionId; // Stream completed
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

  return returnedSessionId;
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
