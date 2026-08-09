import { Message } from '@/types/chat';
import { cn } from '@/lib/utils';
import { Bot, User } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
  isLoading?: boolean;
}

export function MessageBubble({ message, isLoading }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isEmptyAssistant = !isUser && !message.content;

  return (
    <div
      className={cn(
        'flex w-full gap-2.5 my-1.5 items-start',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center shrink-0 text-zinc-300 shadow-sm mt-0.5">
          <Bot className="w-3.5 h-3.5" />
        </div>
      )}

      <div
        className={cn(
          'max-w-[85%] sm:max-w-[75%] rounded-2xl px-3.5 py-2 text-sm transition-all duration-150 shadow-sm flex flex-col justify-between',
          isUser
            ? 'bg-white text-zinc-950 rounded-tr-xs font-medium border border-zinc-200'
            : 'bg-zinc-900 text-zinc-100 rounded-tl-xs border border-zinc-800/90'
        )}
      >
        {isEmptyAssistant ? (
          <div className="flex items-center gap-2 py-0.5 px-0.5">
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce"></span>
            </div>
            <span className="text-xs font-medium text-zinc-400 animate-pulse tracking-wide ml-1">
              Thinking...
            </span>
          </div>
        ) : (
          <p className="whitespace-pre-wrap break-words leading-normal">{message.content}</p>
        )}

        <time
          className={cn(
            "mt-1 block text-[10px] text-right opacity-60 shrink-0 select-none",
            isUser ? "text-zinc-600" : "text-zinc-500"
          )}
        >
          {message.timestamp.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </time>
      </div>

      {isUser && (
        <div className="w-7 h-7 rounded-full bg-zinc-100 text-zinc-900 border border-zinc-300 flex items-center justify-center shrink-0 shadow-sm mt-0.5">
          <User className="w-3.5 h-3.5" />
        </div>
      )}
    </div>
  );
}



