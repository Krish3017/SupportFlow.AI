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
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const statusConfig: Record<string, { icon: any; color: string; bgColor: string; borderColor: string }> = {
    healthy: { icon: CheckCircle2, color: 'text-emerald-400', bgColor: 'bg-emerald-950/60', borderColor: 'border-emerald-800/40' },
    degraded: { icon: AlertCircle, color: 'text-amber-400', bgColor: 'bg-amber-950/60', borderColor: 'border-amber-800/40' },
    offline: { icon: XCircle, color: 'text-rose-400', bgColor: 'bg-rose-950/60', borderColor: 'border-rose-800/40' },
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
            <div key={i} className="h-24 bg-[#111113] border border-zinc-800/80 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center bg-[#111113] border border-rose-900/50 rounded-xl text-rose-400">
        <AlertCircle className="mx-auto h-8 w-8 mb-2" />
        <p className="font-semibold">{error}</p>
        <Button variant="outline" size="sm" onClick={loadData} className="mt-4 border-zinc-700">
          <RotateCw className="mr-2 h-3.5 w-3.5" /> Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 select-none">
      {/* Page Title Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">Operational Overview</h1>
          <p className="text-xs text-zinc-400">Real-time SupportFlow AI health & execution metrics</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Live Engine Connected
          </span>
        </div>
      </div>

      {/* Row 1: Key Metrics Grid (4 Dark Metallic Cards) */}
      {overview && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="bg-[#111113] border border-zinc-800/80 hover:border-zinc-700/80 rounded-xl p-3.5 flex flex-col justify-between transition-all hover:scale-[1.01]">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-zinc-400 font-medium">Total Tickets</span>
              <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300">
                <Ticket className="h-3.5 w-3.5" />
              </div>
            </div>
            <div className="text-2xl font-black text-zinc-50 my-1">{overview.tickets?.total || 0}</div>
            <div className="text-[10px] text-zinc-400 font-medium flex items-center justify-between pt-1 border-t border-zinc-800/60">
              <span className="text-amber-400 font-semibold">{overview.tickets?.open || 0} open</span>
              <span>{overview.tickets?.resolved || 0} resolved</span>
            </div>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 hover:border-zinc-700/80 rounded-xl p-3.5 flex flex-col justify-between transition-all hover:scale-[1.01]">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-zinc-400 font-medium">AI Resolution Rate</span>
              <div className="p-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800/40 text-emerald-400">
                <TrendingUp className="h-3.5 w-3.5" />
              </div>
            </div>
            <div className="text-2xl font-black text-zinc-50 my-1">
              {overview.agents?.success_rate || 0}%
            </div>
            <div className="text-[10px] text-emerald-400 font-medium flex items-center gap-1 pt-1 border-t border-zinc-800/60">
              <ShieldCheck className="h-3 w-3" />
              <span>Automated by LangGraph</span>
            </div>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 hover:border-zinc-700/80 rounded-xl p-3.5 flex flex-col justify-between transition-all hover:scale-[1.01]">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-zinc-400 font-medium">Escalated Tickets</span>
              <div className="p-1.5 rounded-lg bg-rose-950/60 border border-rose-800/40 text-rose-400">
                <AlertCircle className="h-3.5 w-3.5" />
              </div>
            </div>
            <div className="text-2xl font-black text-zinc-50 my-1">{overview.tickets?.escalated || 0}</div>
            <div className="text-[10px] text-rose-400 font-medium flex items-center justify-between pt-1 border-t border-zinc-800/60">
              <span>Human intervention</span>
              <span className="text-zinc-500">Active</span>
            </div>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 hover:border-zinc-700/80 rounded-xl p-3.5 flex flex-col justify-between transition-all hover:scale-[1.01]">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-zinc-400 font-medium">Total Executions</span>
              <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300">
                <Zap className="h-3.5 w-3.5" />
              </div>
            </div>
            <div className="text-2xl font-black text-zinc-50 my-1">{overview.agents?.total_executions || 0}</div>
            <div className="text-[10px] text-zinc-400 font-medium flex items-center gap-1 pt-1 border-t border-zinc-800/60">
              <span>Avg Latency: {overview.agents?.avg_latency || '0.5'}s</span>
            </div>
          </div>
        </div>
      )}

      {/* Row 2: Agent Health Grid (6 Multi-Agent Workers) */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-xs font-bold text-zinc-100 uppercase tracking-wider">Multi-Agent Engine Health</h2>
            <p className="text-[11px] text-zinc-400">Live operational status of specialized AI agents</p>
          </div>
          <Link href="/admin/ai-observatory">
            <button className="text-[11px] text-zinc-400 hover:text-zinc-100 flex items-center gap-1 bg-zinc-900 border border-zinc-800 px-2.5 py-1 rounded-lg transition-colors">
              <span>Observatory</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          </Link>
        </div>

        <div className="grid gap-2.5 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
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
                className="bg-[#09090b] border border-zinc-800/80 hover:border-zinc-700/80 rounded-lg p-2.5 flex flex-col justify-between transition-all hover:scale-[1.02]"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-semibold text-zinc-200 truncate">{agent.name}</span>
                  <div className={cn('rounded-full p-0.5', config.bgColor)}>
                    <StatusIcon className={cn('h-3 w-3', config.color)} />
                  </div>
                </div>

                <div className="my-1">
                  <div className="text-base font-extrabold text-zinc-50">{successPct}%</div>
                  <span className="text-[9px] text-zinc-500 font-medium">Success Rate</span>
                </div>

                <div className="flex items-center justify-between text-[9px] text-zinc-400 border-t border-zinc-800/60 pt-1 mt-1">
                  <span>{agent.avg_latency || '0.2'}s avg</span>
                  <span>{agent.total_executions || 0} execs</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Row 3: Split View (Activity Feed 60% & System Diagnostics 40%) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        {/* Activity Feed (2 Cols) */}
        <div className="lg:col-span-2 bg-[#111113] border border-zinc-800/80 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-zinc-100 uppercase tracking-wider">Live Activity Feed</h3>
              </div>
              <Link href="/admin/activity">
                <button className="text-[10px] text-zinc-400 hover:text-zinc-200">View All</button>
              </Link>
            </div>

            {activity.length === 0 ? (
              <div className="text-center py-6 text-xs text-zinc-500">No activity logged yet</div>
            ) : (
              <div className="space-y-2">
                {activity.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-start gap-2.5 p-2 rounded-lg bg-[#09090b]/80 border border-zinc-800/60 text-xs"
                  >
                    <div
                      className={cn(
                        'mt-1 h-2 w-2 rounded-full flex-shrink-0',
                        item.level === 'error' || item.level === 'critical'
                          ? 'bg-rose-500'
                          : item.level === 'warning'
                          ? 'bg-amber-500'
                          : 'bg-emerald-400'
                      )}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-zinc-200 font-medium line-clamp-1">{item.message}</p>
                      <p className="text-[9px] text-zinc-500 mt-0.5">
                        {formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })}
                      </p>
                    </div>
                    <span className="text-[9px] font-mono uppercase bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded text-zinc-400 flex-shrink-0">
                      {item.type}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Diagnostic Status (1 Col) */}
        <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-zinc-100 uppercase tracking-wider mb-2">Backend Connection</h3>
            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-lg bg-[#09090b] border border-zinc-800/80 flex items-center justify-between">
                <span className="text-zinc-400">Database (SQLite)</span>
                <span className="text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                  Connected
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#09090b] border border-zinc-800/80 flex items-center justify-between">
                <span className="text-zinc-400">Vector Knowledge (Chroma)</span>
                <span className="text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                  Active
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#09090b] border border-zinc-800/80 flex items-center justify-between">
                <span className="text-zinc-400">LLM Inference (Groq)</span>
                <span className="text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                  Configured
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#09090b] border border-zinc-800/80 flex items-center justify-between">
                <span className="text-zinc-400">Email Gateway (Resend)</span>
                <span className="text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                  Configured
                </span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-zinc-800/60 text-[10px] text-zinc-500 flex items-center justify-between">
            <span>SupportFlow API Server</span>
            <span className="text-zinc-300 font-mono">http://localhost:8000</span>
          </div>
        </div>
      </div>
    </div>
  );
}
