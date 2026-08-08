'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DetailDrawer } from '@/components/ui/detail-drawer';
import { fetchConversations, fetchConversationDetail } from '@/lib/api-client';
import { Mail, MessageSquare, Send, Search, RotateCw, ChevronRight, User, Bot } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedChannel, setSelectedChannel] = useState('chat');
  const [selectedConv, setSelectedConv] = useState<any>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Reset selected conversation on channel change to guarantee state isolation
    setSelectedConv(null);
    setIsDrawerOpen(false);
    loadConversations();
  }, [selectedChannel, searchQuery]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const result = await fetchConversations({
        channel: selectedChannel,
        search: searchQuery || undefined,
        limit: 50,
      });
      setConversations(result.conversations || []);
      setError(null);
    } catch (err) {
      setError('Failed to load conversations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = async (id: string) => {
    try {
      setDrawerLoading(true);
      setIsDrawerOpen(true);
      const detail = await fetchConversationDetail(id);
      setSelectedConv(detail);
    } catch (err) {
      console.error('Failed to load conversation detail:', err);
    } finally {
      setDrawerLoading(false);
    }
  };

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">Conversations</h1>
          <p className="text-xs text-zinc-400">Multi-channel support threads (Chat, Email, Telegram)</p>
        </div>
        <button
          onClick={loadConversations}
          className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
        >
          <RotateCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Channel Tabs & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        {/* Channel Tab Selector */}
        <div className="flex items-center bg-[#111113] border border-zinc-800 p-1 rounded-xl gap-1">
          {[
            { id: 'chat', label: 'Web Chat', icon: MessageSquare },
            { id: 'email', label: 'Email', icon: Mail },
            { id: 'telegram', label: 'Telegram', icon: Send },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = selectedChannel === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedChannel(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all',
                  isActive
                    ? 'bg-zinc-800 text-zinc-50 shadow-sm border border-zinc-700/60'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40'
                )}
              >
                <Icon className={cn('h-3.5 w-3.5', isActive ? 'text-emerald-400' : 'text-zinc-400')} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search threads..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#111113] border border-zinc-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-400 animate-pulse">
            Loading {selectedChannel} conversations...
          </div>
        ) : error ? (
          <div className="py-8 text-center text-rose-400 text-xs">{error}</div>
        ) : conversations.length === 0 ? (
          <div className="py-12 text-center text-zinc-500 text-xs">
            No active conversations found for {selectedChannel} channel
          </div>
        ) : (
          <div className="border border-zinc-800/80 rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs text-zinc-300 border-collapse">
              <thead className="bg-[#09090b] text-[10px] text-zinc-500 font-bold uppercase tracking-wider border-b border-zinc-800/80">
                <tr>
                  <th className="py-2.5 px-3">Customer / Session</th>
                  <th className="py-2.5 px-3">Channel</th>
                  <th className="py-2.5 px-3">Messages</th>
                  <th className="py-2.5 px-3">Last Active</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 font-medium">
                {conversations.map((conv) => (
                  <tr
                    key={conv.id}
                    onClick={() => selectConversation(conv.id)}
                    className="hover:bg-zinc-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-zinc-100">
                        {conv.customer?.email || conv.customer_id || 'Anonymous Customer'}
                      </div>
                      {conv.ticket_id && (
                        <div className="text-[10px] text-zinc-500 font-mono">Ticket #{conv.ticket_id}</div>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-[10px] uppercase font-mono text-zinc-400">
                        {conv.channel || selectedChannel}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-zinc-400">
                      {conv.message_count || 0} messages
                    </td>
                    <td className="py-2.5 px-3 text-zinc-400 text-[11px]">
                      {conv.started_at
                        ? formatDistanceToNow(new Date(conv.started_at), { addSuffix: true })
                        : 'Recently'}
                    </td>
                    <td className="py-2.5 px-3">
                      <span
                        className={cn(
                          'text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize',
                          conv.status === 'open' || conv.status === 'active'
                            ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800/40'
                            : 'bg-zinc-900 text-zinc-400 border-zinc-800'
                        )}
                      >
                        {conv.status || 'active'}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <ChevronRight className="h-4 w-4 text-zinc-500 group-hover:text-zinc-200 inline-block" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* In-Context Side Drawer for Conversation Inspection */}
      <DetailDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        title={`Conversation Details`}
        subtitle={selectedConv?.customer?.email || 'Message Thread'}
        widthClass="max-w-xl"
      >
        {drawerLoading ? (
          <div className="py-12 text-center text-zinc-400 text-xs animate-pulse">
            Loading conversation messages...
          </div>
        ) : selectedConv ? (
          <div className="space-y-4">
            {/* Meta Header */}
            <div className="p-3 bg-[#111113] border border-zinc-800 rounded-lg text-xs space-y-1">
              <div className="flex justify-between text-zinc-400">
                <span>Customer:</span>
                <span className="font-semibold text-zinc-100">{selectedConv.customer?.email || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-zinc-400">
                <span>Channel:</span>
                <span className="uppercase font-mono text-zinc-300">{selectedConv.channel}</span>
              </div>
            </div>

            {/* Chat Bubbles */}
            <div className="space-y-3 pt-2">
              {selectedConv.messages?.length === 0 ? (
                <div className="text-center py-6 text-zinc-500">No messages in this thread</div>
              ) : (
                selectedConv.messages?.map((msg: any) => {
                  const isUser = msg.role === 'user';
                  return (
                    <div
                      key={msg.id}
                      className={cn('flex items-start gap-2 text-xs', isUser ? 'flex-row-reverse' : 'flex-row')}
                    >
                      <div
                        className={cn(
                          'h-6 w-6 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0',
                          isUser ? 'bg-zinc-800 text-zinc-200' : 'bg-emerald-950 text-emerald-300 border border-emerald-800/40'
                        )}
                      >
                        {isUser ? <User className="h-3 w-3" /> : <Bot className="h-3 w-3" />}
                      </div>
                      <div
                        className={cn(
                          'max-w-[80%] rounded-xl p-3 border text-xs leading-relaxed',
                          isUser
                            ? 'bg-zinc-800/90 text-zinc-100 border-zinc-700/80'
                            : 'bg-[#111113] text-zinc-200 border-zinc-800'
                        )}
                      >
                        <p>{msg.content}</p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-zinc-500 text-xs">No details found</div>
        )}
      </DetailDrawer>
    </div>
  );
}
