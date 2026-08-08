'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchAgentHealth, fetchExecutions, fetchExecutionDetail } from '@/lib/api-client';
import { DetailDrawer } from '@/components/ui/detail-drawer';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  RotateCw,
  ChevronRight,
  Zap,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  User,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

// ─── helpers ────────────────────────────────────────────────────────────────

function fmtDuration(s: number): string {
  if (!s || s <= 0) return '—';
  if (s < 1) return `${Math.round(s * 1000)}ms`;
  return `${s.toFixed(2)}s`;
}

function fmtMs(s: number): string {
  if (!s || s <= 0) return '—';
  const ms = Math.round(s * 1000);
  return `${ms}ms`;
}

function shortId(id: string): string {
  if (!id) return '—';
  return id.length > 16 ? `${id.substring(0, 16)}…` : id;
}

function channelLabel(ch?: string): string {
  if (!ch) return '—';
  return ch.charAt(0).toUpperCase() + ch.slice(1);
}

// ─── agent icon mapping ──────────────────────────────────────────────────────

const AGENT_ICONS: Record<string, string> = {
  intent_agent: '🎯',
  customer_intelligence_agent: '👤',
  priority_agent: '⚡',
  knowledge_agent: '📚',
  resolution_agent: '💬',
  escalation_agent: '🔺',
};

function agentIcon(agentId?: string): string {
  if (!agentId) return '✦';
  return AGENT_ICONS[agentId] || '✦';
}

// ─── parse step output into readable summary ─────────────────────────────────

function parseStepSummary(agentId: string, raw?: string): Record<string, string> | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (agentId === 'intent_agent') {
      const out: Record<string, string> = {};
      if (parsed.intent) out['Intent'] = parsed.intent.replace(/_/g, ' ');
      if (parsed.sentiment) out['Sentiment'] = parsed.sentiment;
      if (parsed.confidence != null) out['Confidence'] = `${Math.round(parsed.confidence * 100)}%`;
      return out;
    }
    if (agentId === 'priority_agent') {
      if (parsed.priority) return { 'Priority': parsed.priority };
    }
    if (agentId === 'escalation_agent') {
      return { 'Escalated': parsed.escalate ? 'Yes' : 'No' };
    }
    if (agentId === 'customer_intelligence_agent' && parsed.context) {
      const ctx = parsed.context;
      const nameMatch = ctx.match(/'name':\s*'([^']+)'/);
      const tierMatch = ctx.match(/'tier':\s*'([^']+)'/);
      const sentMatch = ctx.match(/'sentiment':\s*'([^']+)'/);
      const out: Record<string, string> = {};
      if (nameMatch) out['Customer'] = nameMatch[1];
      if (tierMatch) out['Tier'] = tierMatch[1];
      if (sentMatch) out['Sentiment'] = sentMatch[1];
      return Object.keys(out).length > 0 ? out : null;
    }
  } catch {
    // Not JSON — treat as plain text summary for resolution agent
  }
  return null;
}

// ─── AgentStep component ─────────────────────────────────────────────────────

function AgentStep({ step, index, total }: { step: any; index: number; total: number }) {
  const [expanded, setExpanded] = useState(false);
  const isLast = index === total - 1;
  const status: 'success' | 'failed' | 'running' | 'skipped' =
    step.status === 'success' ? 'success'
      : step.status === 'failed' ? 'failed'
        : step.status === 'running' ? 'running'
          : 'skipped';

  const summary = parseStepSummary(step.agent_id || '', step.output_summary);
  const isResolutionAgent = step.agent_id === 'resolution_agent';
  const resolutionPreview = isResolutionAgent && step.output_summary
    ? step.output_summary.replace(/^\{[^}]*\}\s*/, '').trim().substring(0, 120)
    : null;

  const statusDot = status === 'success'
    ? 'bg-emerald-400'
    : status === 'failed'
      ? 'bg-rose-500'
      : status === 'running'
        ? 'bg-amber-400 animate-pulse'
        : 'bg-zinc-600';

  return (
    <div className="flex gap-3">
      {/* Timeline spine */}
      <div className="flex flex-col items-center flex-shrink-0">
        <div className={cn('h-2 w-2 rounded-full mt-[14px] flex-shrink-0', statusDot)} />
        {!isLast && <div className="w-px flex-1 bg-zinc-800 mt-1 mb-0 min-h-[20px]" />}
      </div>

      {/* Step card */}
      <div className="flex-1 pb-3 min-w-0">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full text-left"
        >
          <div className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-zinc-800/50 transition-colors group">
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-sm leading-none select-none flex-shrink-0">
                {agentIcon(step.agent_id)}
              </span>
              <span className="text-[12px] font-semibold text-zinc-100 truncate">
                {step.agent_name}
              </span>
              {status === 'failed' && (
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded border bg-rose-950/60 text-rose-400 border-rose-800/40 uppercase flex-shrink-0">
                  Failed
                </span>
              )}
              {status === 'skipped' && (
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded border bg-zinc-900 text-zinc-500 border-zinc-800 uppercase flex-shrink-0">
                  Skipped
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 flex-shrink-0 ml-2">
              <span className="text-[11px] font-mono text-zinc-400 tabular-nums">
                {fmtMs(step.duration)}
              </span>
              {expanded
                ? <ChevronUp className="h-3 w-3 text-zinc-600 group-hover:text-zinc-400" />
                : <ChevronDown className="h-3 w-3 text-zinc-600 group-hover:text-zinc-400" />
              }
            </div>
          </div>
        </button>

        {/* Collapsed summary — always visible */}
        {!expanded && (
          <div className="px-3 pb-1">
            {summary && (
              <div className="flex flex-wrap gap-x-4 gap-y-0.5">
                {Object.entries(summary).map(([k, v]) => (
                  <span key={k} className="text-[10px] text-zinc-500">
                    <span className="text-zinc-600">{k}</span>{' '}
                    <span className="text-zinc-400 font-medium">{v}</span>
                  </span>
                ))}
              </div>
            )}
            {isResolutionAgent && resolutionPreview && (
              <p className="text-[10px] text-zinc-500 italic truncate mt-0.5">
                "{resolutionPreview}…"
              </p>
            )}
            {step.error && (
              <p className="text-[10px] text-rose-400 mt-0.5 truncate">{step.error}</p>
            )}
          </div>
        )}

        {/* Expanded detail */}
        {expanded && (
          <div className="px-3 pb-2 space-y-2">
            {summary && (
              <div className="grid grid-cols-3 gap-2">
                {Object.entries(summary).map(([k, v]) => (
                  <div key={k} className="bg-zinc-900/60 border border-zinc-800/60 rounded-md px-2 py-1.5">
                    <span className="text-[9px] text-zinc-600 uppercase font-bold block">{k}</span>
                    <span className="text-[11px] text-zinc-200 font-semibold capitalize">{v}</span>
                  </div>
                ))}
              </div>
            )}
            {isResolutionAgent && step.output_summary && (
              <div className="bg-zinc-900/60 border border-zinc-800/60 rounded-md p-2.5">
                <span className="text-[9px] text-zinc-600 uppercase font-bold block mb-1">Response Preview</span>
                <p className="text-[11px] text-zinc-300 leading-relaxed">
                  {step.output_summary.substring(0, 300)}
                  {step.output_summary.length > 300 && '…'}
                </p>
              </div>
            )}
            {!summary && !isResolutionAgent && step.output_summary && (
              <div className="bg-zinc-900/60 border border-zinc-800/60 rounded-md p-2.5">
                <span className="text-[9px] text-zinc-600 uppercase font-bold block mb-1">Output</span>
                <p className="text-[11px] text-zinc-400 font-mono leading-relaxed break-all">
                  {step.output_summary.substring(0, 400)}
                </p>
              </div>
            )}
            {step.error && (
              <div className="bg-rose-950/30 border border-rose-900/40 rounded-md p-2.5">
                <span className="text-[9px] text-rose-500 uppercase font-bold block mb-1">Error</span>
                <p className="text-[11px] text-rose-400 leading-relaxed">{step.error}</p>
              </div>
            )}
            {step.input_summary && (
              <details className="group">
                <summary className="text-[10px] text-zinc-600 hover:text-zinc-400 cursor-pointer list-none flex items-center gap-1 select-none">
                  <ChevronRight className="h-3 w-3 group-open:rotate-90 transition-transform" />
                  View input
                </summary>
                <p className="text-[10px] text-zinc-600 font-mono mt-1 pl-4 break-all">
                  {step.input_summary}
                </p>
              </details>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Execution Detail Panel ──────────────────────────────────────────────────

function ExecutionDetailPanel({ exec }: { exec: any }) {
  const steps: any[] = exec.steps || [];
  const successCount = steps.filter((s) => s.status === 'success').length;
  const successRate = steps.length > 0
    ? Math.round((successCount / steps.length) * 100)
    : 100;

  const overallStatus = exec.status === 'completed' || exec.status === 'success'
    ? 'completed'
    : exec.status === 'failed'
      ? 'failed'
      : exec.status;

  const statusColor = overallStatus === 'completed'
    ? 'text-emerald-400'
    : overallStatus === 'failed'
      ? 'text-rose-400'
      : 'text-amber-400';

  const convShort = exec.conversation_id ? shortId(exec.conversation_id) : '—';
  const custName = exec.customer_id
    ? shortId(exec.customer_id)
    : '—';

  return (
    <div className="space-y-5">
      {/* Context header */}
      <div className="space-y-1 pb-4 border-b border-zinc-800/60">
        <div className="flex items-center gap-2 text-[10px] text-zinc-500">
          <MessageSquare className="h-3 w-3" />
          <span className="font-mono">{convShort}</span>
          {exec.intent && (
            <>
              <span className="text-zinc-700">·</span>
              <span className="capitalize">{exec.intent.replace(/_/g, ' ')}</span>
            </>
          )}
          {exec.escalated && (
            <>
              <span className="text-zinc-700">·</span>
              <span className="text-amber-400 font-semibold">Escalated</span>
            </>
          )}
        </div>
        {exec.customer_id && (
          <div className="flex items-center gap-2 text-[10px] text-zinc-600">
            <User className="h-3 w-3" />
            <span className="font-mono">{exec.customer_id}</span>
          </div>
        )}
      </div>

      {/* Compact metrics row */}
      <div className="grid grid-cols-4 gap-2">
        <div className="bg-zinc-900/50 border border-zinc-800/60 rounded-lg p-2.5 text-center">
          <span className="text-[9px] text-zinc-600 uppercase font-bold block mb-1">Status</span>
          <span className={cn('text-[11px] font-bold capitalize', statusColor)}>{overallStatus}</span>
        </div>
        <div className="bg-zinc-900/50 border border-zinc-800/60 rounded-lg p-2.5 text-center">
          <span className="text-[9px] text-zinc-600 uppercase font-bold block mb-1">Duration</span>
          <span className="text-[11px] font-bold text-zinc-200 font-mono tabular-nums">
            {fmtDuration(exec.total_duration)}
          </span>
        </div>
        <div className="bg-zinc-900/50 border border-zinc-800/60 rounded-lg p-2.5 text-center">
          <span className="text-[9px] text-zinc-600 uppercase font-bold block mb-1">Agents</span>
          <span className="text-[11px] font-bold text-zinc-200">{steps.length}</span>
        </div>
        <div className="bg-zinc-900/50 border border-zinc-800/60 rounded-lg p-2.5 text-center">
          <span className="text-[9px] text-zinc-600 uppercase font-bold block mb-1">Success</span>
          <span className={cn(
            'text-[11px] font-bold',
            successRate === 100 ? 'text-emerald-400' : successRate >= 50 ? 'text-amber-400' : 'text-rose-400'
          )}>
            {successRate}%
          </span>
        </div>
      </div>

      {/* Priority + sentiment chips if present */}
      {(exec.priority || exec.sentiment || exec.confidence != null) && (
        <div className="flex items-center gap-2 flex-wrap">
          {exec.priority && (
            <span className="text-[10px] px-2 py-0.5 rounded border border-zinc-800 bg-zinc-900 text-zinc-400">
              Priority: <span className="text-zinc-200 font-semibold capitalize">{exec.priority}</span>
            </span>
          )}
          {exec.sentiment && (
            <span className="text-[10px] px-2 py-0.5 rounded border border-zinc-800 bg-zinc-900 text-zinc-400">
              Sentiment: <span className="text-zinc-200 font-semibold capitalize">{exec.sentiment}</span>
            </span>
          )}
          {exec.confidence != null && (
            <span className="text-[10px] px-2 py-0.5 rounded border border-zinc-800 bg-zinc-900 text-zinc-400">
              Confidence: <span className="text-zinc-200 font-semibold">{Math.round(exec.confidence * 100)}%</span>
            </span>
          )}
        </div>
      )}

      {/* Agent timeline */}
      {steps.length > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] text-zinc-600 uppercase font-bold tracking-wider">
              Agent Workflow
            </span>
            <span className="text-[9px] text-zinc-700 italic">
              approx. timing
            </span>
          </div>
          <div className="rounded-xl border border-zinc-800/60 bg-zinc-900/20 overflow-hidden">
            <div className="px-2 pt-2 pb-1">
              {steps.map((step, i) => (
                <AgentStep key={i} step={step} index={i} total={steps.length} />
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-6 text-[11px] text-zinc-600">
          No agent steps recorded for this execution.
        </div>
      )}
    </div>
  );
}

// ─── Execution table row ─────────────────────────────────────────────────────

function ExecutionRow({ exec, onSelect }: { exec: any; onSelect: () => void }) {
  const status = exec.status === 'completed' || exec.status === 'success'
    ? 'completed'
    : exec.status === 'failed'
      ? 'failed'
      : exec.status;

  const statusStyle = status === 'completed'
    ? 'bg-emerald-950/50 text-emerald-400 border-emerald-900/40'
    : status === 'failed'
      ? 'bg-rose-950/50 text-rose-400 border-rose-900/40'
      : 'bg-amber-950/50 text-amber-400 border-amber-900/40';

  // Conversation reference — prefer short ID
  const convRef = exec.conversation_id ? shortId(exec.conversation_id) : '—';
  // Customer — short ID if present
  const custRef = exec.customer_id ? shortId(exec.customer_id) : null;

  return (
    <tr
      onClick={onSelect}
      className="hover:bg-zinc-800/30 cursor-pointer transition-colors group border-b border-zinc-800/50 last:border-0"
    >
      {/* Execution ID */}
      <td className="py-2.5 px-3">
        <span className="font-mono text-[11px] text-zinc-500 group-hover:text-zinc-300 transition-colors">
          {shortId(exec.id)}
        </span>
      </td>

      {/* Conversation / Customer */}
      <td className="py-2.5 px-3">
        <div className="flex flex-col gap-0.5 min-w-0">
          <div className="flex items-center gap-1.5">
            <MessageSquare className="h-3 w-3 text-zinc-700 flex-shrink-0" />
            <span className="text-[11px] font-mono text-zinc-400 truncate">{convRef}</span>
          </div>
          {custRef && (
            <div className="flex items-center gap-1.5">
              <User className="h-3 w-3 text-zinc-700 flex-shrink-0" />
              <span className="text-[10px] font-mono text-zinc-600 truncate">{custRef}</span>
            </div>
          )}
        </div>
      </td>

      {/* Intent + channel */}
      <td className="py-2.5 px-3 hidden md:table-cell">
        <div className="flex flex-col gap-0.5">
          {exec.intent && (
            <span className="text-[11px] text-zinc-400 capitalize">{exec.intent.replace(/_/g, ' ')}</span>
          )}
          {exec.escalated ? (
            <span className="text-[9px] text-amber-500 font-semibold">↑ escalated</span>
          ) : null}
        </div>
      </td>

      {/* Steps */}
      <td className="py-2.5 px-3 hidden sm:table-cell">
        <span className="text-[11px] text-zinc-500 tabular-nums">{exec.step_count || 0}</span>
      </td>

      {/* Duration */}
      <td className="py-2.5 px-3">
        <span className="text-[11px] font-mono text-zinc-300 tabular-nums">
          {fmtDuration(exec.total_duration)}
        </span>
      </td>

      {/* Status */}
      <td className="py-2.5 px-3">
        <span className={cn('text-[9px] font-bold px-2 py-0.5 rounded-full border capitalize', statusStyle)}>
          {status}
        </span>
      </td>

      {/* Action */}
      <td className="py-2.5 px-3 text-right">
        <ChevronRight className="h-3.5 w-3.5 text-zinc-700 group-hover:text-zinc-300 inline-block transition-colors" />
      </td>
    </tr>
  );
}

// ─── Agent Telemetry Card ────────────────────────────────────────────────────

function AgentTelemetryCard({ agent }: { agent: any }) {
  const total = agent.total_executions || 0;
  const success = agent.successful_executions || 0;
  const rate = total > 0 ? Math.round((success / total) * 100) : 100;

  const statusConfig: Record<string, { color: string; dot: string }> = {
    healthy: { color: 'text-emerald-400', dot: 'bg-emerald-400' },
    degraded: { color: 'text-amber-400', dot: 'bg-amber-400' },
    offline: { color: 'text-rose-400', dot: 'bg-rose-500' },
  };
  const cfg = statusConfig[agent.status] || statusConfig.healthy;

  return (
    <div className="bg-[#111113] border border-zinc-800/70 hover:border-zinc-700/80 rounded-xl p-3 flex flex-col justify-between transition-colors">
      <div className="flex items-start justify-between mb-2">
        <span className="text-[11px] font-semibold text-zinc-200 leading-tight pr-2">{agent.name}</span>
        <div className={cn('h-1.5 w-1.5 rounded-full mt-1 flex-shrink-0', cfg.dot)} />
      </div>
      <div>
        <div className={cn('text-lg font-extrabold tabular-nums', rate === 100 ? 'text-zinc-50' : cfg.color)}>
          {rate}%
        </div>
        <div className="text-[9px] text-zinc-600 font-medium mt-0.5">success rate</div>
      </div>
      <div className="flex items-center justify-between mt-2 pt-2 border-t border-zinc-800/50 text-[9px] text-zinc-600 font-medium">
        <span>{fmtMs(agent.avg_latency)} avg</span>
        <span>{total} exec</span>
      </div>
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function AIObservatoryPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<any>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [agentResult, execResult] = await Promise.all([
        fetchAgentHealth(),
        fetchExecutions({ limit: 50 }),
      ]);
      setAgents(agentResult.agents || []);
      setExecutions(execResult.executions || []);
      setError(null);
    } catch (err) {
      setError('Failed to load observatory data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const selectExecution = async (id: string) => {
    setDrawerLoading(true);
    setIsDrawerOpen(true);
    setSelectedExecution(null);
    try {
      const detail = await fetchExecutionDetail(id);
      setSelectedExecution(detail);
    } catch (err) {
      console.error('Failed to load execution detail:', err);
    } finally {
      setDrawerLoading(false);
    }
  };

  const closeDrawer = () => {
    setIsDrawerOpen(false);
    setSelectedExecution(null);
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-5 w-40 bg-zinc-800 rounded" />
        <div className="grid gap-2 grid-cols-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-24 bg-[#111113] border border-zinc-800 rounded-xl" />
          ))}
        </div>
        <div className="h-64 bg-[#111113] border border-zinc-800 rounded-xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center bg-[#111113] border border-rose-900/40 rounded-xl text-rose-400">
        <AlertCircle className="mx-auto h-7 w-7 mb-2" />
        <p className="text-sm font-semibold">{error}</p>
        <button
          onClick={loadData}
          className="mt-4 px-3 py-1.5 bg-zinc-800 rounded-lg text-xs text-zinc-300 hover:text-zinc-100"
        >
          Retry
        </button>
      </div>
    );
  }

  // Build the drawer subtitle from real data
  const drawerSubtitle = selectedExecution
    ? `conv: ${shortId(selectedExecution.conversation_id || '')} · ${fmtDuration(selectedExecution.total_duration)}`
    : undefined;

  return (
    <div className="space-y-6 select-none">
      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">AI Observatory</h1>
          <p className="text-xs text-zinc-500">Execution traces · agent latencies · workflow telemetry</p>
        </div>
        <button
          onClick={loadData}
          className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-100 flex items-center gap-1.5 text-xs transition-colors"
        >
          <RotateCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* ── Agent Telemetry ── */}
      {agents.length > 0 && (
        <div>
          <span className="text-[10px] text-zinc-600 uppercase font-bold tracking-wider">Agent Telemetry</span>
          <div className="grid gap-2.5 mt-2 grid-cols-2 sm:grid-cols-3 lg:grid-cols-6">
            {agents.map((agent) => (
              <AgentTelemetryCard key={agent.id} agent={agent} />
            ))}
          </div>
        </div>
      )}

      {/* ── Execution Log ── */}
      <div className="bg-[#111113] border border-zinc-800/70 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/60">
          <div className="flex items-center gap-2">
            <Zap className="h-3.5 w-3.5 text-zinc-500" />
            <span className="text-[11px] font-bold text-zinc-300 uppercase tracking-wider">
              Execution Log
            </span>
          </div>
          <span className="text-[10px] text-zinc-600">{executions.length} traces</span>
        </div>

        {executions.length === 0 ? (
          <div className="py-14 text-center text-[11px] text-zinc-600">
            No executions recorded yet
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#0d0d0f]">
                <th className="py-2 px-3 text-[9px] text-zinc-600 font-bold uppercase tracking-wider">Execution</th>
                <th className="py-2 px-3 text-[9px] text-zinc-600 font-bold uppercase tracking-wider">Conversation</th>
                <th className="py-2 px-3 text-[9px] text-zinc-600 font-bold uppercase tracking-wider hidden md:table-cell">Intent</th>
                <th className="py-2 px-3 text-[9px] text-zinc-600 font-bold uppercase tracking-wider hidden sm:table-cell">Agents</th>
                <th className="py-2 px-3 text-[9px] text-zinc-600 font-bold uppercase tracking-wider">Duration</th>
                <th className="py-2 px-3 text-[9px] text-zinc-600 font-bold uppercase tracking-wider">Status</th>
                <th className="py-2 px-3 text-right" />
              </tr>
            </thead>
            <tbody>
              {executions.map((exec) => (
                <ExecutionRow
                  key={exec.id}
                  exec={exec}
                  onSelect={() => selectExecution(exec.id)}
                />
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Detail Drawer ── */}
      <DetailDrawer
        isOpen={isDrawerOpen}
        onClose={closeDrawer}
        title="Execution Trace"
        subtitle={drawerSubtitle}
        widthClass="max-w-xl"
      >
        {drawerLoading ? (
          <div className="space-y-4 animate-pulse">
            <div className="grid grid-cols-4 gap-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-14 bg-zinc-800/60 rounded-lg" />
              ))}
            </div>
            <div className="h-4 bg-zinc-800/60 rounded w-1/3" />
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-10 bg-zinc-800/40 rounded-lg" />
            ))}
          </div>
        ) : selectedExecution ? (
          <ExecutionDetailPanel exec={selectedExecution} />
        ) : (
          <div className="py-12 text-center text-[11px] text-zinc-600">
            No execution details available
          </div>
        )}
      </DetailDrawer>
    </div>
  );
}
