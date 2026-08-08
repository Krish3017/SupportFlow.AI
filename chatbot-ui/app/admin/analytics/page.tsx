'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { fetchAnalyticsOverview, fetchTicketAnalytics, fetchAgentAnalytics } from '@/lib/api-client';
import { RotateCw, BarChart3, TrendingUp, ShieldCheck, Ticket, Users, Zap } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [ticketAnalytics, setTicketAnalytics] = useState<any>(null);
  const [agentAnalytics, setAgentAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'support' | 'ai'>('support');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewRes, ticketRes, agentRes] = await Promise.all([
        fetchAnalyticsOverview(),
        fetchTicketAnalytics(),
        fetchAgentAnalytics(),
      ]);
      setOverview(overviewRes);
      setTicketAnalytics(ticketRes);
      setAgentAnalytics(agentRes);
      setError(null);
    } catch (err) {
      setError('Failed to load analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-xs text-zinc-400 animate-pulse">Loading analytics charts...</div>;
  }

  if (error) {
    return <div className="py-8 text-center text-rose-400 text-xs">{error}</div>;
  }

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">Analytics & Insights</h1>
          <p className="text-xs text-zinc-400">Support tickets distribution, agent performance & channel trends</p>
        </div>
        <button
          onClick={loadData}
          className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
        >
          <RotateCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Top Metrics Cards */}
      {overview && (
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 md:grid-cols-5">
          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">Total Tickets</span>
            <div className="text-xl font-extrabold text-zinc-50 my-1">{overview.tickets?.total || 0}</div>
            <span className="text-[9px] text-zinc-500">All Time</span>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">Resolved</span>
            <div className="text-xl font-extrabold text-emerald-400 my-1">{overview.tickets?.resolved || 0}</div>
            <span className="text-[9px] text-emerald-500">Resolved Rate</span>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">Escalated</span>
            <div className="text-xl font-extrabold text-rose-400 my-1">{overview.tickets?.escalated || 0}</div>
            <span className="text-[9px] text-zinc-500">Human Escalations</span>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">AI Success</span>
            <div className="text-xl font-extrabold text-zinc-50 my-1">{overview.agents?.success_rate || 0}%</div>
            <span className="text-[9px] text-emerald-400 font-medium">Groq LLM + LangGraph</span>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">Customers</span>
            <div className="text-xl font-extrabold text-zinc-50 my-1">{overview.customers?.total || 0}</div>
            <span className="text-[9px] text-zinc-500 font-medium">Active Profiles</span>
          </div>
        </div>
      )}

      {/* Tab Selector */}
      <div className="flex items-center gap-2 bg-[#111113] border border-zinc-800 p-1 rounded-xl w-fit">
        <button
          onClick={() => setActiveTab('support')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'support'
              ? 'bg-zinc-800 text-zinc-50 border border-zinc-700/60'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          Support Trends
        </button>
        <button
          onClick={() => setActiveTab('ai')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'ai'
              ? 'bg-zinc-800 text-zinc-50 border border-zinc-700/60'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          AI Agent Latencies & Errors
        </button>
      </div>

      {/* Chart Section */}
      {activeTab === 'support' && ticketAnalytics && (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
            <h3 className="text-xs font-bold text-zinc-200 uppercase tracking-wider mb-3">Tickets by Priority</h3>
            <div className="h-64">
              {ticketAnalytics.by_priority?.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={ticketAnalytics.by_priority}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="priority" stroke="#71717a" fontSize={11} />
                    <YAxis stroke="#71717a" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', borderRadius: '8px' }} />
                    <Bar dataKey="count" fill="#34d399" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs text-zinc-500">No ticket priority data</div>
              )}
            </div>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
            <h3 className="text-xs font-bold text-zinc-200 uppercase tracking-wider mb-3">Tickets by Channel</h3>
            <div className="h-64">
              {ticketAnalytics.by_channel?.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={ticketAnalytics.by_channel}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="channel" stroke="#71717a" fontSize={11} />
                    <YAxis stroke="#71717a" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', borderRadius: '8px' }} />
                    <Bar dataKey="count" fill="#60a5fa" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs text-zinc-500">No ticket channel data</div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'ai' && agentAnalytics && (
        <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
          <h3 className="text-xs font-bold text-zinc-200 uppercase tracking-wider mb-3">AI Agent Executions Breakdown</h3>
          <div className="h-72">
            {agentAnalytics.by_agent?.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={agentAnalytics.by_agent}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="agent_name" stroke="#71717a" fontSize={11} />
                  <YAxis stroke="#71717a" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', borderRadius: '8px' }} />
                  <Bar dataKey="success" fill="#34d399" name="Success" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="failed" fill="#f43f5e" name="Failed" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-zinc-500">No agent execution data</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
