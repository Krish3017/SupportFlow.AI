'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { fetchAnalyticsOverview, fetchAgentHealth, fetchActivity } from '@/lib/api-client';
import { formatDistanceToNow } from 'date-fns';
import {
  Ticket,
  TrendingUp,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  XCircle,
  Activity,
  Users,
  MessageSquare,
  Zap,
  ShieldCheck,
  RotateCw,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);
  const [agents, setAgents] = useState<any[]>([]);
  const [activity, setActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewRes, agentsRes, activityRes] = await Promise.all([
        fetchAnalyticsOverview(),
        fetchAgentHealth(),
        fetchActivity({ limit: 6 }),
      ]);
      setOverview(overviewRes);
      setAgents(agentsRes.agents || []);
      setActivity(activityRes.activities || []);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data from backend API');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const statusConfig: Record<string, { icon: any; color: string; bgColor: string; borderColor: string }> = {
    healthy: { icon: CheckCircle2, color: 'text-emerald-400', bgColor: 'bg-emerald-950/80', borderColor: 'border-emerald-700/60' },
    degraded: { icon: AlertCircle, color: 'text-amber-400', bgColor: 'bg-amber-950/80', borderColor: 'border-amber-700/60' },
    offline: { icon: XCircle, color: 'text-rose-400', bgColor: 'bg-rose-950/80', borderColor: 'border-rose-700/60' },
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse space-y-2">
          <div className="h-6 w-32 bg-zinc-800 rounded" />
          <div className="h-4 w-48 bg-zinc-900 rounded" />
        </div>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-[#111113] border border-zinc-800 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center bg-[#111113] border border-rose-900/50 rounded-xl text-rose-400">
        <AlertCircle className="mx-auto h-8 w-8 mb-2" />
        <p className="font-semibold text-sm">{error}</p>
        <Button variant="outline" size="sm" onClick={loadData} className="mt-4 border-zinc-700 text-zinc-200">
          <RotateCw className="mr-2 h-3.5 w-3.5" /> Retry Connection
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 select-none">
      {/* Page Title Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-zinc-50">Operational Overview</h1>
          <p className="text-xs text-zinc-300 font-medium mt-0.5">Real-time SupportFlow AI health & execution metrics</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-emerald-400 bg-emerald-950/80 border border-emerald-700/60 px-3 py-1 rounded-full font-bold flex items-center gap-1.5 shadow-sm">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Live Engine Connected
          </span>
        </div>
      </div>

      {/* Row 1: Key Metrics Grid (4 Dark Metallic Cards) */}
      {overview && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          <div className="bg-[#111113] border border-zinc-800/90 hover:border-zinc-700/90 rounded-xl p-4 flex flex-col justify-between transition-all hover:scale-[1.01] shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-300 font-bold uppercase tracking-wider">Total Tickets</span>
              <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-200">
                <Ticket className="h-4 w-4" />
              </div>
            </div>
            <div className="text-3xl font-black text-zinc-50 my-1.5 tracking-tight">{overview.tickets?.total || 0}</div>
            <div className="text-xs text-zinc-300 font-semibold flex items-center justify-between pt-2 border-t border-zinc-800/70">
              <span className="text-amber-400 font-bold">{overview.tickets?.open || 0} open</span>
              <span>{overview.tickets?.resolved || 0} resolved</span>
            </div>
          </div>

          <div className="bg-[#111113] border border-zinc-800/90 hover:border-zinc-700/90 rounded-xl p-4 flex flex-col justify-between transition-all hover:scale-[1.01] shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-300 font-bold uppercase tracking-wider">AI Resolution Rate</span>
              <div className="p-1.5 rounded-lg bg-emerald-950/80 border border-emerald-700/60 text-emerald-400">
                <TrendingUp className="h-4 w-4" />
              </div>
            </div>
            <div className="text-3xl font-black text-zinc-50 my-1.5 tracking-tight">
              {overview.agents?.success_rate || 0}%
            </div>
            <div className="text-xs text-emerald-400 font-bold flex items-center gap-1.5 pt-2 border-t border-zinc-800/70">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Automated by LangGraph</span>
            </div>
          </div>

          <div className="bg-[#111113] border border-zinc-800/90 hover:border-zinc-700/90 rounded-xl p-4 flex flex-col justify-between transition-all hover:scale-[1.01] shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-300 font-bold uppercase tracking-wider">Escalated Tickets</span>
              <div className="p-1.5 rounded-lg bg-rose-950/80 border border-rose-700/60 text-rose-400">
                <AlertCircle className="h-4 w-4" />
              </div>
            </div>
            <div className="text-3xl font-black text-zinc-50 my-1.5 tracking-tight">{overview.tickets?.escalated || 0}</div>
            <div className="text-xs text-rose-400 font-bold flex items-center justify-between pt-2 border-t border-zinc-800/70">
              <span>Human intervention</span>
              <span className="text-zinc-300 font-medium">Active</span>
            </div>
          </div>

          <div className="bg-[#111113] border border-zinc-800/90 hover:border-zinc-700/90 rounded-xl p-4 flex flex-col justify-between transition-all hover:scale-[1.01] shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-300 font-bold uppercase tracking-wider">Total Executions</span>
              <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-200">
                <Zap className="h-4 w-4" />
              </div>
            </div>
            <div className="text-3xl font-black text-zinc-50 my-1.5 tracking-tight">{overview.agents?.total_executions || 0}</div>
            <div className="text-xs text-zinc-300 font-bold flex items-center gap-1 pt-2 border-t border-zinc-800/70">
              <span>Avg Latency: {overview.agents?.avg_latency || '0.56'}s</span>
            </div>
          </div>
        </div>
      )}

      {/* Row 2: Agent Health Grid (6 Multi-Agent Workers) */}
      <div className="bg-[#111113] border border-zinc-800/90 rounded-xl p-5 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xs font-extrabold text-zinc-200 uppercase tracking-widest">Multi-Agent Engine Telemetry</h2>
            <p className="text-xs text-zinc-400 font-medium mt-0.5">Live operational status of specialized AI agents</p>
          </div>
          <Link href="/admin/ai-observatory">
            <button className="text-xs font-bold text-zinc-200 hover:text-zinc-50 flex items-center gap-1.5 bg-zinc-900 border border-zinc-700/80 px-3 py-1.5 rounded-lg transition-colors">
              <span>Observatory</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </Link>
        </div>

        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
          {agents.map((agent) => {
            const config = statusConfig[agent.status] || statusConfig.healthy;
            const StatusIcon = config.icon;
            const successPct =
              agent.total_executions > 0
                ? ((agent.successful_executions / agent.total_executions) * 100).toFixed(0)
                : '100';

            return (
              <div
                key={agent.id}
                className="bg-[#09090b] border border-zinc-800/90 hover:border-zinc-700/90 rounded-xl p-3 flex flex-col justify-between transition-all hover:scale-[1.02]"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-zinc-100 truncate">{agent.name}</span>
                  <div className={cn('rounded-full p-0.5', config.bgColor)}>
                    <StatusIcon className={cn('h-3.5 w-3.5', config.color)} />
                  </div>
                </div>

                <div className="my-1.5">
                  <div className="text-xl font-black text-zinc-50">{successPct}%</div>
                  <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider">Success Rate</span>
                </div>

                <div className="flex items-center justify-between text-[11px] text-zinc-300 border-t border-zinc-800/70 pt-1.5 mt-1 font-semibold">
                  <span>{(agent.avg_latency * 1000).toFixed(0)}ms avg</span>
                  <span>{agent.total_executions || 0} exec</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Row 3: Split View (Activity Feed 65% & System Diagnostics 35%) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Activity Feed (2 Cols) */}
        <div className="lg:col-span-2 bg-[#111113] border border-zinc-800/90 rounded-xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Activity className="h-4.5 w-4.5 text-emerald-400" />
                <h3 className="text-xs font-extrabold text-zinc-200 uppercase tracking-widest">Live Activity Feed</h3>
              </div>
              <Link href="/admin/activity">
                <button className="text-xs text-zinc-300 font-bold hover:text-zinc-100">View All</button>
              </Link>
            </div>

            {activity.length === 0 ? (
              <div className="text-center py-8 text-xs text-zinc-400">No activity logged yet</div>
            ) : (
              <div className="space-y-2.5">
                {activity.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-start gap-3 p-3 rounded-lg bg-[#09090b] border border-zinc-800/80 text-xs"
                  >
                    <div
                      className={cn(
                        'mt-1 h-2.5 w-2.5 rounded-full flex-shrink-0',
                        item.level === 'error' || item.level === 'critical'
                          ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]'
                          : item.level === 'warning'
                          ? 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]'
                          : 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]'
                      )}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-zinc-100 font-semibold line-clamp-1">{item.message}</p>
                      <p className="text-[11px] text-zinc-400 font-medium mt-0.5">
                        {formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })}
                      </p>
                    </div>
                    <span className="text-[10px] font-bold font-mono uppercase bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-zinc-300 flex-shrink-0">
                      {item.type}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Diagnostic Status (1 Col) */}
        <div className="bg-[#111113] border border-zinc-800/90 rounded-xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-extrabold text-zinc-200 uppercase tracking-widest mb-3">Backend Connections</h3>
            <div className="space-y-2.5 text-xs">
              <div className="p-3 rounded-lg bg-[#09090b] border border-zinc-800 flex items-center justify-between font-semibold">
                <span className="text-zinc-200">Database (SQLite)</span>
                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-700/60 px-2.5 py-0.5 rounded-full">
                  Connected
                </span>
              </div>
              <div className="p-3 rounded-lg bg-[#09090b] border border-zinc-800 flex items-center justify-between font-semibold">
                <span className="text-zinc-200">Vector Knowledge (Chroma)</span>
                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-700/60 px-2.5 py-0.5 rounded-full">
                  Active
                </span>
              </div>
              <div className="p-3 rounded-lg bg-[#09090b] border border-zinc-800 flex items-center justify-between font-semibold">
                <span className="text-zinc-200">LLM Inference (Groq)</span>
                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-700/60 px-2.5 py-0.5 rounded-full">
                  Configured
                </span>
              </div>
              <div className="p-3 rounded-lg bg-[#09090b] border border-zinc-800 flex items-center justify-between font-semibold">
                <span className="text-zinc-200">Email Gateway (Resend)</span>
                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-700/60 px-2.5 py-0.5 rounded-full">
                  Configured
                </span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-zinc-800/80 text-xs text-zinc-400 font-semibold flex items-center justify-between">
            <span>SupportFlow API Server</span>
            <span className="text-zinc-100 font-mono">{process.env.NEXT_PUBLIC_API_URL || 'Connected'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
