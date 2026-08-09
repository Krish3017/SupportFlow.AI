import { useState, useRef, useEffect, useCallback, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { ArrowUp } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export function MessageInput({
  onSendMessage,
  disabled = false,
  placeholder = 'Type your request...',
  className = '',
}: MessageInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = '24px';
    const newHeight = Math.min(Math.max(textarea.scrollHeight, 24), 180);
    textarea.style.height = `${newHeight}px`;
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [input, adjustHeight]);

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = '24px';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const hasText = Boolean(input.trim());

  return (
    <div
      className={`relative flex items-end w-full gap-2.5 rounded-2xl bg-[#141418]/85 backdrop-blur-xl border border-white/10 focus-within:border-indigo-500/40 focus-within:shadow-[0_0_25px_rgba(99,102,241,0.15)] transition-all duration-200 px-3.5 py-2.5 sm:py-3 ${className}`}
    >
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="flex-1 bg-transparent text-zinc-100 placeholder:text-zinc-500 text-sm sm:text-base focus:outline-none resize-none min-h-[24px] max-h-[180px] leading-6 py-0.5"
        style={{ overflowY: input.split('\n').length > 5 ? 'auto' : 'hidden' }}
      />

      <Button
        onClick={handleSend}
        disabled={disabled || !hasText}
        size="icon"
        type="button"
        className={`h-8 w-8 rounded-xl shrink-0 transition-all duration-200 ${
          hasText && !disabled
            ? 'bg-white text-zinc-950 hover:bg-zinc-200 shadow-md cursor-pointer scale-100'
            : 'bg-white/10 text-zinc-600 cursor-not-allowed opacity-60'
        }`}
      >
        <ArrowUp className="h-4 w-4" />
        <span className="sr-only">Send</span>
      </Button>
    </div>
  );
}



