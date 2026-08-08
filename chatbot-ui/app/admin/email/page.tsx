'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DetailDrawer } from '@/components/ui/detail-drawer';
import { fetchEmails, fetchEmailDetail, sendEmailReply, retryEmail } from '@/lib/api-client';
import { Search, Mail, RefreshCw, Send, RotateCw, ChevronRight } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

export default function EmailPage() {
  const [emails, setEmails] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEmail, setSelectedEmail] = useState<any>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
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
        limit: 50,
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
      setDrawerLoading(true);
      setIsDrawerOpen(true);
      const detail = await fetchEmailDetail(id);
      setSelectedEmail(detail);
    } catch (err) {
      console.error('Failed to load email:', err);
    } finally {
      setDrawerLoading(false);
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
      case 'resolved':
        return 'bg-emerald-950/60 text-emerald-400 border-emerald-800/40';
      case 'escalated':
        return 'bg-rose-950/60 text-rose-400 border-rose-800/40';
      case 'pending':
        return 'bg-amber-950/60 text-amber-400 border-amber-800/40';
      case 'error':
        return 'bg-rose-950/60 text-rose-400 border-rose-800/40';
      default:
        return 'bg-zinc-900 text-zinc-400 border-zinc-800';
    }
  };

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">Email Center</h1>
          <p className="text-xs text-zinc-400">Inbound Gmail polling tickets & automated Resend replies</p>
        </div>
        <button
          onClick={loadEmails}
          className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
        >
          <RotateCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Tabs & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center bg-[#111113] border border-zinc-800 p-1 rounded-xl gap-1">
          {['all', 'pending', 'resolved', 'escalated', 'error'].map((tab) => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all',
                statusFilter === tab
                  ? 'bg-zinc-800 text-zinc-50 border border-zinc-700/60'
                  : 'text-zinc-400 hover:text-zinc-200'
              )}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search email subject or sender..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#111113] border border-zinc-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
          />
        </div>
      </div>

      {/* Emails Table */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-400 animate-pulse">Loading email tickets...</div>
        ) : error ? (
          <div className="py-8 text-center text-rose-400 text-xs">{error}</div>
        ) : emails.length === 0 ? (
          <div className="py-12 text-center text-zinc-500 text-xs">No email tickets found</div>
        ) : (
          <div className="border border-zinc-800/80 rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs text-zinc-300 border-collapse">
              <thead className="bg-[#09090b] text-[10px] text-zinc-500 font-bold uppercase tracking-wider border-b border-zinc-800/80">
                <tr>
                  <th className="py-2.5 px-3">Subject</th>
                  <th className="py-2.5 px-3">Sender</th>
                  <th className="py-2.5 px-3">Received</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 font-medium">
                {emails.map((email) => (
                  <tr
                    key={email.id}
                    onClick={() => selectEmail(email.id)}
                    className="hover:bg-zinc-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-2.5 px-3 font-semibold text-zinc-100 line-clamp-1">{email.subject}</td>
                    <td className="py-2.5 px-3 text-zinc-400 font-mono text-[11px]">{email.sender_email}</td>
                    <td className="py-2.5 px-3 text-zinc-400 text-[11px]">
                      {email.created_at ? formatDistanceToNow(new Date(email.created_at), { addSuffix: true }) : 'Recently'}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={cn('text-[9px] font-bold px-2 py-0.5 rounded-full border uppercase', getStatusColor(email.status))}>
                        {email.status}
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

      {/* In-Context Side Drawer for Email Inspection & Manual Reply */}
      <DetailDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        title="Email Ticket Inspection"
        subtitle={selectedEmail?.subject || 'Loading email...'}
        widthClass="max-w-xl"
      >
        {drawerLoading ? (
          <div className="py-12 text-center text-zinc-400 text-xs animate-pulse">Loading email content...</div>
        ) : selectedEmail ? (
          <div className="space-y-4">
            <div className="p-3 bg-[#111113] border border-zinc-800 rounded-lg text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-zinc-500">From:</span>
                <span className="font-mono text-zinc-200">{selectedEmail.sender_email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Subject:</span>
                <span className="font-semibold text-zinc-100">{selectedEmail.subject}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-500">Status:</span>
                <div className="flex items-center gap-2">
                  <span className={cn('px-2 py-0.5 rounded-full border text-[9px] font-bold uppercase', getStatusColor(selectedEmail.status))}>
                    {selectedEmail.status}
                  </span>
                  {selectedEmail.status === 'error' && (
                    <button
                      onClick={() => handleRetry(selectedEmail.id)}
                      className="px-2 py-0.5 bg-zinc-800 text-zinc-200 rounded text-[10px] flex items-center gap-1 hover:bg-zinc-700"
                    >
                      <RefreshCw className="h-3 w-3" /> Retry
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Email Inbound Body */}
            <div className="bg-[#111113] border border-zinc-800 p-3 rounded-lg text-xs">
              <span className="text-[10px] text-zinc-500 font-bold uppercase block mb-1">Inbound Body</span>
              <p className="text-zinc-300 whitespace-pre-wrap leading-relaxed">{selectedEmail.body}</p>
            </div>

            {/* Automated AI Response */}
            {selectedEmail.ai_response && (
              <div className="bg-emerald-950/40 border border-emerald-800/60 p-3 rounded-lg text-xs space-y-1">
                <span className="text-[10px] text-emerald-400 font-bold uppercase block">Automated AI Resolution</span>
                <p className="text-emerald-200 whitespace-pre-wrap leading-relaxed">{selectedEmail.ai_response}</p>
              </div>
            )}

            {/* Manual Outbound Reply */}
            <div className="pt-3 border-t border-zinc-800 space-y-2">
              <span className="text-[10px] text-zinc-400 font-bold uppercase block">Send Manual Reply via Resend API</span>
              <textarea
                placeholder="Type manual response to send directly to customer..."
                value={replyBody}
                onChange={(e) => setReplyBody(e.target.value)}
                rows={4}
                className="w-full bg-[#111113] border border-zinc-800 rounded-lg p-2.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-700"
              />
              <button
                onClick={handleReply}
                disabled={sending || !replyBody.trim()}
                className="px-3 py-1.5 bg-emerald-950 border border-emerald-800 text-emerald-300 rounded-lg text-xs font-bold hover:bg-emerald-900 flex items-center gap-1.5 transition-colors"
              >
                <Send className="h-3.5 w-3.5" />
                <span>{sending ? 'Sending via Resend...' : 'Send Outbound Reply'}</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-zinc-500 text-xs">No email selected</div>
        )}
      </DetailDrawer>
    </div>
  );
}
