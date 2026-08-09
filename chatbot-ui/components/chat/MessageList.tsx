import { Message } from '@/types/chat';
import { MessageBubble } from './MessageBubble';
import { useEffect, useRef, useState, useCallback } from 'react';
import { ArrowDown } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [userScrolledUp, setUserScrolledUp] = useState(false);

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    
    // User is considered scrolled up if more than 100px from bottom
    if (distanceFromBottom > 100) {
      setUserScrolledUp(true);
    } else {
      setUserScrolledUp(false);
    }
  }, []);

  const scrollToBottom = useCallback((smooth = true) => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto',
      });
    }
    setUserScrolledUp(false);
  }, []);

  // Smart Auto-scroll: Only scroll down if user has not manually scrolled up
  useEffect(() => {
    if (!userScrolledUp) {
      scrollToBottom(false);
    }
  }, [messages, userScrolledUp, scrollToBottom]);


  return (
    <div className="relative h-full w-full flex flex-col min-h-0">
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 min-h-0 overflow-y-auto px-4 md:px-10 max-w-5xl mx-auto w-full scroll-smooth"
      >
        <div className="flex flex-col py-4 space-y-4">

          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} isLoading={isLoading} />
          ))}
          <div ref={bottomRef} className="h-1 w-full shrink-0" />
        </div>
      </div>

      {/* Floating Jump to Bottom Button */}

      {userScrolledUp && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20">
          <Button
            onClick={() => scrollToBottom(true)}
            size="sm"
            className="rounded-full bg-zinc-900 hover:bg-zinc-800 text-zinc-100 border border-zinc-700 shadow-2xl text-xs gap-1.5 px-3.5 py-1.5 backdrop-blur-md transition-all duration-200"
          >
            <ArrowDown className="w-3.5 h-3.5" />
            <span>New response ↓</span>
          </Button>
        </div>
      )}
    </div>
  );

}

