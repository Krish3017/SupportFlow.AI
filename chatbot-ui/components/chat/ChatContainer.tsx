'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useTheme } from 'next-themes';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Message } from '@/types/chat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Moon, Sun, Loader2 } from 'lucide-react';
import {
  sendChatMessage,
  fetchConversationHistory,
  fetchSessionConversation,
} from '@/lib/api';

const STORAGE_KEYS = {
  SESSION_ID: 'supportflow_session_id',
  CONVERSATION_ID: 'supportflow_conversation_id',
} as const;

function getStoredSessionId(): string {
  if (typeof window === 'undefined') return '';
  let sessionId = localStorage.getItem(STORAGE_KEYS.SESSION_ID);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEYS.SESSION_ID, sessionId);
  }
  return sessionId;
}

function getStoredConversationId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(STORAGE_KEYS.CONVERSATION_ID);
}

function storeConversationId(id: string) {
  localStorage.setItem(STORAGE_KEYS.CONVERSATION_ID, id);
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(true);
  const { theme, setTheme } = useTheme();
  const sessionIdRef = useRef<string>('');
  const conversationIdRef = useRef<string | null>(null);
  const restoredRef = useRef(false);

  const restoreSession = useCallback(async () => {
    if (restoredRef.current) return;
    restoredRef.current = true;

    const sessionId = getStoredSessionId();
    sessionIdRef.current = sessionId;

    const storedConvId = getStoredConversationId();

    if (storedConvId) {
      const history = await fetchConversationHistory(storedConvId);
      if (history && history.status !== 'closed' && history.status !== 'archived') {
        conversationIdRef.current = storedConvId;
        const restored: Message[] = history.messages.map((m) => ({
          id: m.id,
          role: m.role as 'user' | 'assistant',
          content: m.content,
          timestamp: new Date(m.timestamp),
        }));
        setMessages(restored);
        setIsRestoring(false);
        return;
      }
    }

    const sessionInfo = await fetchSessionConversation(sessionId);
    if (sessionInfo.conversation_id) {
      const history = await fetchConversationHistory(sessionInfo.conversation_id);
      if (history && history.status !== 'closed' && history.status !== 'archived') {
        conversationIdRef.current = sessionInfo.conversation_id;
        storeConversationId(sessionInfo.conversation_id);
        const restored: Message[] = history.messages.map((m) => ({
          id: m.id,
          role: m.role as 'user' | 'assistant',
          content: m.content,
          timestamp: new Date(m.timestamp),
        }));
        setMessages(restored);
      }
    }

    setIsRestoring(false);
  }, []);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const result = await sendChatMessage(
        content,
        sessionIdRef.current,
        'C001',
        (chunk) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        }
      );

      if (result.session_id) {
        sessionIdRef.current = result.session_id;
        localStorage.setItem(STORAGE_KEYS.SESSION_ID, result.session_id);
      }

      if (result.conversation_id) {
        conversationIdRef.current = result.conversation_id;
        storeConversationId(result.conversation_id);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content:
                  'Sorry, I encountered an error. Please make sure the backend server is running.',
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-4xl h-[600px] flex flex-col shadow-lg">
      <div className="px-6 py-4 border-b bg-muted/40 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Customer Support</h2>
          <p className="text-sm text-muted-foreground">
            AI-powered assistance
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="ml-4"
        >
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </div>

      <div className="flex-1 overflow-hidden">
        {isRestoring ? (
          <div className="h-full flex items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <MessageList messages={messages} />
        )}
      </div>

      <MessageInput onSendMessage={handleSendMessage} disabled={isLoading || isRestoring} />
    </Card>
  );
}
