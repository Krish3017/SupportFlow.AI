import { ChatContainer } from '@/components/chat/ChatContainer';

export default function ChatPage() {
  return (
    <main className="w-screen h-screen overflow-hidden bg-ruixen-glow text-slate-100 flex flex-col relative dark">
      <ChatContainer />
    </main>
  );
}
