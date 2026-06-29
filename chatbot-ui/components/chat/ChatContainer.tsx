'use client';

import { useState, useRef, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Message } from '@/types/chat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Moon, Sun } from 'lucide-react';
import { sendChatMessage } from '@/lib/api';

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { theme, setTheme } = useTheme();
  const sessionIdRef = useRef<string | null>(null);

  // Generate session_id once when component mounts
  useEffect(() => {
    if (!sessionIdRef.current) {
      sessionIdRef.current = crypto.randomUUID();
    }
  }, []);

  const handleSendMessage = async (content: string) => {
    // Create user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Create placeholder assistant message for streaming
    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);

    try {
      // Stream response from backend
      const returnedSessionId = await sendChatMessage(
        content,
        sessionIdRef.current!,
        'C001',
        (chunk) => {
          // Update the assistant message with each chunk
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        }
      );

      // Update session_id if returned from backend
      if (returnedSessionId) {
        sessionIdRef.current = returnedSessionId;
      }
    } catch (error) {
      console.error('Failed to send message:', error);

      // Update message with error
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
      {/* Chat header */}
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

      {/* Messages area */}
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} />
      </div>

      {/* Input area */}
      <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </Card>
  );
}
