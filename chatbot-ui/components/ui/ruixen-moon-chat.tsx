"use client";

import { MessageInput } from "@/components/chat/MessageInput";
import { Bot, Zap } from "lucide-react";


interface RuixenMoonChatProps {
  onSendMessage?: (content: string) => void;
  disabled?: boolean;
}

export default function RuixenMoonChat({ onSendMessage, disabled = false }: RuixenMoonChatProps) {
  const handleSend = (content: string) => {
    if (onSendMessage) {
      onSendMessage(content);
    }
  };

  return (
    <div className="relative w-full h-full text-zinc-100 flex flex-col items-center justify-between select-none overflow-hidden font-sans">


      {/* Centered Hero Content with Sharp Bold Typography & Glowing Backdrop */}
      <div className="z-10 w-full max-w-4xl flex flex-col items-center justify-center px-4 text-center my-auto">
        {/* Futuristic Badge */}

        <div className="max-w-2xl mx-auto space-y-4">
          <h1 className="animate-hero-fade text-5xl sm:text-7xl font-sharp-heading tracking-tight text-gradient-sharp drop-shadow-[0_4px_24px_rgba(99,102,241,0.25)]">
            SupportFlow AI
          </h1>
          <p className="animate-hero-delay-1 text-base sm:text-lg text-zinc-400 font-normal tracking-tight leading-relaxed max-w-xl mx-auto">
            Experience next-generation autonomous customer support. Ask questions, check orders, or manage requests instantly.
          </p>
        </div>

        {/* Compact Floating Composer */}
        <div className="animate-hero-delay-2 w-full max-w-2xl px-2 mt-8">
          <MessageInput
            onSendMessage={handleSend}
            disabled={disabled}
            placeholder="Type your request or question..."
          />
        </div>

        {/* Feature Highlights */}
        <div className="mt-8 flex items-center justify-center gap-6 text-xs text-zinc-500 font-medium animate-hero-delay-2">
          <span className="flex items-center gap-1.5 hover:text-zinc-300 transition-colors">
            <Zap className="w-3.5 h-3.5 text-amber-400" /> Instant RAG Search
          </span>
          <span className="w-1 h-1 rounded-full bg-zinc-700" />
          <span className="flex items-center gap-1.5 hover:text-zinc-300 transition-colors">
            <Bot className="w-3.5 h-3.5 text-indigo-400" /> Autonomous Escalation
          </span>
        </div>
      </div>

      {/* Bottom spacing */}
      <div className="h-12 shrink-0" />
    </div>
  );
}

