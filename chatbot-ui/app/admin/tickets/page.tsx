'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DetailDrawer } from '@/components/ui/detail-drawer';
import { fetchTickets } from '@/lib/api-client';
import { Search, LayoutGrid, List, RotateCw, Ticket, ChevronRight, AlertCircle, Clock, CheckCircle2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

export default function TicketsPage() {
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'table' | 'kanban'>('table');
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedTicket, setSelectedTicket] = useState<any>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  useEffect(() => {
    loadTickets();
  }, [searchQuery, priorityFilter, statusFilter]);

  const loadTickets = async () => {
    try {
      setLoading(true);
      const result = await fetchTickets({
        status: statusFilter === 'all' ? undefined : statusFilter,
        priority: priorityFilter === 'all' ? undefined : priorityFilter,
        search: searchQuery || undefined,
        limit: 100,
      });
      setTickets(result.tickets || []);
      setError(null);
    } catch (err) {
      setError('Failed to load tickets');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-rose-950/80 text-rose-400 border-rose-800/60';
      case 'high':
        return 'bg-amber-950/80 text-amber-400 border-amber-800/60';
      case 'medium':
        return 'bg-blue-950/80 text-blue-400 border-blue-800/60';
      default:
        return 'bg-zinc-900 text-zinc-400 border-zinc-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new':
        return 'bg-blue-950/60 text-blue-400 border-blue-800/40';
      case 'in_progress':
        return 'bg-amber-950/60 text-amber-400 border-amber-800/40';
      case 'resolved':
        return 'bg-emerald-950/60 text-emerald-400 border-emerald-800/40';
      case 'escalated':
        return 'bg-rose-950/60 text-rose-400 border-rose-800/40';
      default:
        return 'bg-zinc-900 text-zinc-400 border-zinc-800';
    }
  };

  const openTicketDrawer = (ticket: any) => {
    setSelectedTicket(ticket);
    setIsDrawerOpen(true);
  };

  const ticketsByStatus = {
    new: tickets.filter((t) => t.status === 'new'),
    in_progress: tickets.filter((t) => t.status === 'in_progress'),
    resolved: tickets.filter((t) => t.status === 'resolved'),
    escalated: tickets.filter((t) => t.status === 'escalated'),
  };

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">Support Tickets</h1>
          <p className="text-xs text-zinc-400">Track and manage customer support requests across channels</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-[#111113] border border-zinc-800 p-0.5 rounded-lg">
            <button
              onClick={() => setView('table')}
              className={cn(
                'p-1.5 rounded transition-colors',
                view === 'table' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-200'
              )}
              title="Table View"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => setView('kanban')}
              className={cn(
                'p-1.5 rounded transition-colors',
                view === 'kanban' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-200'
              )}
              title="Kanban Board"
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
          </div>
          <button
            onClick={loadTickets}
            className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
          >
            <RotateCw className="h-3.5 w-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search tickets by ID or subject..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#111113] border border-zinc-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-[#111113] border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-zinc-700"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#111113] border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-zinc-700"
          >
            <option value="all">All Statuses</option>
            <option value="new">New</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="escalated">Escalated</option>
          </select>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-400 animate-pulse">Loading support tickets...</div>
        ) : error ? (
          <div className="py-8 text-center text-rose-400 text-xs">{error}</div>
        ) : tickets.length === 0 ? (
          <div className="py-12 text-center text-zinc-500 text-xs">No tickets match current filters</div>
        ) : view === 'table' ? (
          <div className="border border-zinc-800/80 rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs text-zinc-300 border-collapse">
              <thead className="bg-[#09090b] text-[10px] text-zinc-500 font-bold uppercase tracking-wider border-b border-zinc-800/80">
                <tr>
                  <th className="py-2.5 px-3">Ticket Subject</th>
                  <th className="py-2.5 px-3">Customer</th>
                  <th className="py-2.5 px-3">Priority</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Channel</th>
                  <th className="py-2.5 px-3">Created</th>
                  <th className="py-2.5 px-3 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 font-medium">
                {tickets.map((t) => (
                  <tr
                    key={t.id}
                    onClick={() => openTicketDrawer(t)}
                    className="hover:bg-zinc-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-zinc-100 line-clamp-1">{t.subject || 'Support Ticket'}</div>
                      <div className="text-[10px] text-zinc-500 font-mono">#{t.id}</div>
                    </td>
                    <td className="py-2.5 px-3 text-zinc-300">{t.customer?.email || t.customer_id || 'Unknown'}</td>
                    <td className="py-2.5 px-3">
                      <span className={cn('text-[9px] font-semibold px-2 py-0.5 rounded-full border uppercase', getPriorityColor(t.priority))}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={cn('text-[9px] font-semibold px-2 py-0.5 rounded-full border uppercase', getStatusColor(t.status))}>
                        {t.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 uppercase font-mono text-[10px] text-zinc-400">{t.channel || 'web'}</td>
                    <td className="py-2.5 px-3 text-zinc-400 text-[11px]">
                      {t.created_at ? formatDistanceToNow(new Date(t.created_at), { addSuffix: true }) : 'Recent'}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <ChevronRight className="h-4 w-4 text-zinc-500 group-hover:text-zinc-200 inline-block" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(ticketsByStatus).map(([statusKey, list]) => (
              <div key={statusKey} className="bg-[#09090b] border border-zinc-800/80 rounded-xl p-3 space-y-2">
                <div className="flex items-center justify-between pb-1 border-b border-zinc-800">
                  <h3 className="text-xs font-bold text-zinc-300 uppercase">{statusKey.replace('_', ' ')}</h3>
                  <span className="text-[10px] font-bold text-zinc-500 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">
                    {list.length}
                  </span>
                </div>
                <div className="space-y-2 pt-1">
                  {list.map((t) => (
                    <div
                      key={t.id}
                      onClick={() => openTicketDrawer(t)}
                      className="bg-[#111113] border border-zinc-800/80 hover:border-zinc-700/80 rounded-lg p-2.5 cursor-pointer transition-all hover:scale-[1.01]"
                    >
                      <div className="text-xs font-semibold text-zinc-100 line-clamp-1 mb-1">{t.subject}</div>
                      <div className="flex items-center justify-between text-[10px]">
                        <span className={cn('px-1.5 py-0.2 rounded border uppercase font-bold text-[9px]', getPriorityColor(t.priority))}>
                          {t.priority}
                        </span>
                        <span className="text-zinc-500 font-mono">#{t.id}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Ticket Details Side Drawer */}
      <DetailDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        title={selectedTicket ? `Ticket #${selectedTicket.id}` : 'Ticket Detail'}
        subtitle={selectedTicket?.subject}
        widthClass="max-w-xl"
      >
        {selectedTicket && (
          <div className="space-y-4">
            <div className="p-3 bg-[#111113] border border-zinc-800 rounded-lg text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-zinc-500">Status:</span>
                <span className={cn('px-2 py-0.5 rounded-full border text-[10px] uppercase font-bold', getStatusColor(selectedTicket.status))}>
                  {selectedTicket.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Priority:</span>
                <span className={cn('px-2 py-0.5 rounded-full border text-[10px] uppercase font-bold', getPriorityColor(selectedTicket.priority))}>
                  {selectedTicket.priority}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Customer Email:</span>
                <span className="font-semibold text-zinc-100">{selectedTicket.customer?.email || selectedTicket.customer_id || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Channel:</span>
                <span className="uppercase font-mono text-zinc-300">{selectedTicket.channel || 'web'}</span>
              </div>
            </div>

            {selectedTicket.description && (
              <div className="bg-[#111113] border border-zinc-800 p-3 rounded-lg text-xs space-y-1">
                <span className="text-[10px] text-zinc-500 font-bold uppercase block">Description / Note</span>
                <p className="text-zinc-300 leading-relaxed">{selectedTicket.description}</p>
              </div>
            )}
          </div>
        )}
      </DetailDrawer>
    </div>
  );
}
