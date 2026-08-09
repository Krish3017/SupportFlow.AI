"use client";

import { MessageInput } from "@/components/chat/MessageInput";

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
    <div className="relative w-full h-screen bg-aurora-canvas text-zinc-100 flex flex-col items-center justify-between select-none overflow-hidden font-sans">
      {/* Ambient Background Layers */}
      <div className="aurora-layer-1" />
      <div className="aurora-light-sweep" />
      <div className="noise-overlay" />

      {/* Top spacing element */}
      <div className="h-16 shrink-0" />

      {/* Centered Hero Content with Subtle Entrance Animations */}
      <div className="z-10 w-full max-w-3xl flex flex-col items-center justify-center px-4 text-center my-auto">
        <div className="max-w-xl mx-auto space-y-3">
          <h1 className="animate-hero-fade text-4xl sm:text-5xl font-bold tracking-tight text-white font-sans drop-shadow-md">
            SupportFlow AI
          </h1>
          <p className="animate-hero-delay-1 text-sm sm:text-base text-zinc-400 font-light tracking-wide leading-relaxed">
            Build something amazing — just start typing below.
          </p>
        </div>

        {/* Compact Floating Composer */}
        <div className="animate-hero-delay-2 w-full max-w-2xl px-2 mt-8">
          <MessageInput
            onSendMessage={handleSend}
            disabled={disabled}
            placeholder="Type your request..."
          />
        </div>
      </div>

      {/* Bottom spacing */}
      <div className="h-16 shrink-0" />
    </div>
  );
}
