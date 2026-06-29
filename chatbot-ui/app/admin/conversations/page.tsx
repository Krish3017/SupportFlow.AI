'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { LoadingState } from '@/components/ui/loading-state';
import { fetchConversations, fetchConversationDetail } from '@/lib/api-client';
import { Mail, MessageSquare, Send, Search } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedChannel, setSelectedChannel] = useState('chat');
  const [selectedConv, setSelectedConv] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadConversations();
  }, [selectedChannel, searchQuery]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const result = await fetchConversations({
        channel: selectedChannel,
        search: searchQuery || undefined,
        limit: 50
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
      const detail = await fetchConversationDetail(id);
      setSelectedConv(detail);
    } catch (err) {
      console.error('Failed to load conversation detail:', err);
    }
  };

  const channelIcons = { email: Mail, chat: MessageSquare, telegram: Send };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Conversations</h1>
        <p className="text-muted-foreground">Multi-channel customer communications</p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search conversations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      <Tabs value={selectedChannel} onValueChange={setSelectedChannel}>
        <TabsList>
          <TabsTrigger value="chat">
            <MessageSquare className="mr-2 size-4" />
            Chat
          </TabsTrigger>
          <TabsTrigger value="email">
            <Mail className="mr-2 size-4" />
            Email
          </TabsTrigger>
          <TabsTrigger value="telegram">
            <Send className="mr-2 size-4" />
            Telegram
          </TabsTrigger>
        </TabsList>

        <TabsContent value={selectedChannel} className="space-y-4">
          {loading ? (
            <LoadingState message="Loading conversations..." />
          ) : error ? (
            <Card className="p-8 text-center text-red-500">{error}</Card>
          ) : conversations.length === 0 ? (
            <Card className="p-8 text-center text-muted-foreground">
              No conversations found
            </Card>
          ) : (
            conversations.map((conversation) => (
              <Card
                key={conversation.id}
                className="p-4 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => selectConversation(conversation.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{conversation.customer.email}</span>
                    <Badge variant="outline" className="text-xs">
                      {conversation.status}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(conversation.started_at), { addSuffix: true })}
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">
                  {conversation.message_count} messages
                  {conversation.ticket_id && ` • Ticket #${conversation.ticket_id}`}
                </div>
              </Card>
            ))
          )}

          {selectedConv && (
            <Card className="p-6 mt-6 border-2">
              <h3 className="font-semibold mb-4">Conversation Detail</h3>
              <div className="space-y-4">
                {selectedConv.messages?.map((message: any) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg p-3 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
