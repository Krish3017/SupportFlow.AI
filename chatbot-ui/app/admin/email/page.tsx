'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoadingState } from '@/components/ui/loading-state';
import { fetchEmails, fetchEmailDetail, sendEmailReply, retryEmail } from '@/lib/api-client';
import { Search, Mail, RefreshCw, Send } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function EmailPage() {
  const [emails, setEmails] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEmail, setSelectedEmail] = useState<any>(null);
  const [replyBody, setReplyBody] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadEmails();
  }, [statusFilter, searchQuery]);

  const loadEmails = async () => {
    try {
      setLoading(true);
      const result = await fetchEmails({
        status: statusFilter === 'all' ? undefined : statusFilter,
        search: searchQuery || undefined,
        limit: 50
      });
      setEmails(result.emails || []);
      setError(null);
    } catch (err) {
      setError('Failed to load emails');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectEmail = async (id: number) => {
    try {
      const detail = await fetchEmailDetail(id);
      setSelectedEmail(detail);
    } catch (err) {
      console.error('Failed to load email:', err);
    }
  };

  const handleReply = async () => {
    if (!selectedEmail || !replyBody.trim()) return;
    try {
      setSending(true);
      await sendEmailReply(
        selectedEmail.sender_email,
        `Re: ${selectedEmail.subject}`,
        replyBody
      );
      setReplyBody('');
      await loadEmails();
    } catch (err) {
      console.error('Reply failed:', err);
    } finally {
      setSending(false);
    }
  };

  const handleRetry = async (emailId: number) => {
    try {
      await retryEmail(emailId);
      await loadEmails();
    } catch (err) {
      console.error('Retry failed:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'bg-green-500/10 text-green-500';
      case 'escalated': return 'bg-red-500/10 text-red-500';
      case 'pending': return 'bg-blue-500/10 text-blue-500';
      case 'error': return 'bg-red-500/10 text-red-500';
      default: return '';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Email Center</h1>
        <p className="text-muted-foreground">Manage inbound and outbound emails</p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search emails..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      <Tabs value={statusFilter} onValueChange={setStatusFilter}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="resolved">Resolved</TabsTrigger>
          <TabsTrigger value="escalated">Escalated</TabsTrigger>
          <TabsTrigger value="error">Failed</TabsTrigger>
        </TabsList>

        <TabsContent value={statusFilter}>
          {loading ? (
            <LoadingState message="Loading emails..." />
          ) : error ? (
            <Card className="p-8 text-center text-red-500">{error}</Card>
          ) : emails.length === 0 ? (
            <Card className="p-8 text-center text-muted-foreground">
              No emails found
            </Card>
          ) : (
            <div className="space-y-3">
              {emails.map((email) => (
                <Card
                  key={email.id}
                  className="p-4 cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => selectEmail(email.id)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Mail className="size-4 text-muted-foreground" />
                        <span className="font-medium text-sm truncate">{email.subject}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{email.sender_email}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <Badge variant="outline" className={getStatusColor(email.status)}>
                        {email.status}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(email.created_at), { addSuffix: true })}
                      </span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {selectedEmail && (
        <Card className="p-6 border-2">
          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold">{selectedEmail.subject}</h3>
                <p className="text-sm text-muted-foreground">From: {selectedEmail.sender_email}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className={getStatusColor(selectedEmail.status)}>
                  {selectedEmail.status}
                </Badge>
                {selectedEmail.status === 'error' && (
                  <Button size="sm" variant="outline" onClick={() => handleRetry(selectedEmail.id)}>
                    <RefreshCw className="mr-1 size-3" />
                    Retry
                  </Button>
                )}
              </div>
            </div>

            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm whitespace-pre-wrap">{selectedEmail.body}</p>
            </div>

            {selectedEmail.ai_response && (
              <div className="p-4 bg-green-500/5 border border-green-500/20 rounded-lg">
                <p className="text-xs font-semibold text-green-600 mb-2">AI Response</p>
                <p className="text-sm whitespace-pre-wrap">{selectedEmail.ai_response}</p>
              </div>
            )}

            <div className="pt-4 border-t">
              <h4 className="font-semibold mb-2">Manual Reply</h4>
              <Textarea
                placeholder="Type your reply..."
                value={replyBody}
                onChange={(e) => setReplyBody(e.target.value)}
                rows={4}
              />
              <Button
                className="mt-2"
                onClick={handleReply}
                disabled={sending || !replyBody.trim()}
              >
                <Send className="mr-2 size-4" />
                {sending ? 'Sending...' : 'Send Reply'}
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
