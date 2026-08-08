'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DetailDrawer } from '@/components/ui/detail-drawer';
import { fetchAgentHealth, fetchExecutions, fetchExecutionDetail } from '@/lib/api-client';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Microscope,
  Zap,
  RotateCw,
  ChevronRight,
  Database,
  Wrench,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function AIObservatoryPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<any>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [agentResult, execResult] = await Promise.all([
        fetchAgentHealth(),
        fetchExecutions({ limit: 25 }),
      ]);
      setAgents(agentResult.agents || []);
      setExecutions(execResult.executions || []);
      setError(null);
    } catch (err) {
      setError('Failed to load observatory data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectExecution = async (id: string) => {
    try {
      setDrawerLoading(true);
      setIsDrawerOpen(true);
      const detail = await fetchExecutionDetail(id);
      setSelectedExecution(detail);
    } catch (err) {
      console.error('Failed to load execution detail:', err);
    } finally {
      setDrawerLoading(false);
    }
  };

  const statusConfig: Record<string, { icon: any; color: string; bgColor: string }> = {
    healthy: { icon: CheckCircle2, color: 'text-emerald-400', bgColor: 'bg-emerald-950/60' },
    degraded: { icon: AlertCircle, color: 'text-amber-400', bgColor: 'bg-amber-950/60' },
    offline: { icon: XCircle, color: 'text-rose-400', bgColor: 'bg-rose-950/60' },
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-6 w-48 bg-zinc-800 rounded animate-pulse" />
        <div className="grid gap-3 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-[#111113] border border-zinc-800 rounded-xl animate-pulse" />
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
        <button onClick={loadData} className="mt-4 px-3 py-1.5 bg-zinc-800 rounded-lg text-xs text-zinc-200">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">AI Observatory</h1>
          <p className="text-xs text-zinc-400">Multi-agent execution traces, latencies & tool calls</p>
        </div>
        <button
          onClick={loadData}
          className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
        >
          <RotateCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Agent Health Grid */}
      <div>
        <h2 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2.5">Agent Telemetry</h2>
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
          {agents.map((agent) => {
            const config = statusConfig[agent.status] || statusConfig.healthy;
            const StatusIcon = config.icon;
            const successRate =
              agent.total_executions > 0
                ? `${((agent.successful_executions / agent.total_executions) * 100).toFixed(0)}%`
                : '100%';

            return (
              <div
                key={agent.id}
                className="bg-[#111113] border border-zinc-800/80 hover:border-zinc-700/80 rounded-xl p-3 flex flex-col justify-between transition-all hover:scale-[1.01]"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-zinc-100 truncate">{agent.name}</span>
                  <div className={cn('rounded-full p-1', config.bgColor)}>
                    <StatusIcon className={cn('h-3.5 w-3.5', config.color)} />
                  </div>
                </div>

                <div className="my-2">
                  <div className="text-xl font-extrabold text-zinc-50">{successRate}</div>
                  <span className="text-[10px] text-zinc-500 font-medium">Success Rate</span>
                </div>

                <div className="flex items-center justify-between text-[10px] text-zinc-400 pt-1.5 border-t border-zinc-800/60 font-medium">
                  <span>{agent.avg_latency || '0.2'}s avg</span>
                  <span>{agent.total_executions || 0} execs</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Executions Table (Click opens In-Context Side Drawer) */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Microscope className="h-4 w-4 text-emerald-400" />
            <h2 className="text-xs font-bold text-zinc-100 uppercase tracking-wider">Execution Logs & Traces</h2>
          </div>
          <span className="text-[10px] text-zinc-500">{executions.length} recent executions</span>
        </div>

        {executions.length === 0 ? (
          <div className="text-center py-10 text-xs text-zinc-500">No executions recorded yet</div>
        ) : (
          <div className="border border-zinc-800/80 rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs text-zinc-300 border-collapse">
              <thead className="bg-[#09090b] text-[10px] text-zinc-500 font-bold uppercase tracking-wider border-b border-zinc-800/80">
                <tr>
                  <th className="py-2.5 px-3">Execution ID</th>
                  <th className="py-2.5 px-3">Ticket ID</th>
                  <th className="py-2.5 px-3">Steps</th>
                  <th className="py-2.5 px-3">Duration</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 font-medium">
                {executions.map((exec) => (
                  <tr
                    key={exec.id}
                    onClick={() => selectExecution(exec.id)}
                    className="hover:bg-zinc-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-2.5 px-3 font-mono text-zinc-400 text-[11px] group-hover:text-zinc-200">
                      {exec.id.substring(0, 14)}...
                    </td>
                    <td className="py-2.5 px-3 text-zinc-200 font-semibold">
                      #{exec.ticket_id || 'N/A'}
                    </td>
                    <td className="py-2.5 px-3 text-zinc-400">
                      <span className="bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-[10px]">
                        {exec.step_count || 1} step(s)
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-zinc-300 font-mono text-[11px]">
                      {exec.total_duration || 0.4}s
                    </td>
                    <td className="py-2.5 px-3">
                      <span
                        className={cn(
                          'text-[10px] font-semibold px-2 py-0.5 rounded-full border',
                          exec.status === 'success' || exec.status === 'completed'
                            ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800/40'
                            : exec.status === 'failed'
                            ? 'bg-rose-950/60 text-rose-400 border-rose-800/40'
                            : 'bg-amber-950/60 text-amber-400 border-amber-800/40'
                        )}
                      >
                        {exec.status}
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

      {/* In-Context Side Drawer for Execution Details */}
      <DetailDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        title={selectedExecution ? `Execution Trace — Ticket #${selectedExecution.ticket_id || 'N/A'}` : 'Execution Trace'}
        subtitle={selectedExecution ? `ID: ${selectedExecution.id}` : 'Loading details...'}
        widthClass="max-w-2xl"
      >
        {drawerLoading ? (
          <div className="py-12 text-center text-zinc-400 text-xs animate-pulse">
            Loading detailed execution trace...
          </div>
        ) : selectedExecution ? (
          <div className="space-y-4">
            {/* Overview Summary Bar */}
            <div className="grid grid-cols-3 gap-2 bg-[#111113] border border-zinc-800 p-3 rounded-lg text-xs">
              <div>
                <span className="text-[10px] text-zinc-500 uppercase font-bold block">Status</span>
                <span className="font-semibold text-emerald-400 capitalize">{selectedExecution.status}</span>
              </div>
              <div>
                <span className="text-[10px] text-zinc-500 uppercase font-bold block">Duration</span>
                <span className="font-semibold text-zinc-200">{selectedExecution.total_duration}s</span>
              </div>
              <div>
                <span className="text-[10px] text-zinc-500 uppercase font-bold block">Total Steps</span>
                <span className="font-semibold text-zinc-200">{selectedExecution.steps?.length || 0}</span>
              </div>
            </div>

            {/* Execution Steps Timeline */}
            <div>
              <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3">Agent Workflow Steps</h4>
              <div className="space-y-3">
                {selectedExecution.steps?.map((step: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3 bg-[#111113] border border-zinc-800 rounded-lg space-y-2 relative"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
                        <span className="font-bold text-zinc-100">{step.agent_name || 'Agent'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono text-zinc-400">{step.duration || 0.1}s</span>
                        <span
                          className={cn(
                            'text-[9px] font-semibold px-2 py-0.2 rounded-full border',
                            step.status === 'success'
                              ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800/40'
                              : 'bg-rose-950/60 text-rose-400 border-rose-800/40'
                          )}
                        >
                          {step.status}
                        </span>
                      </div>
                    </div>

                    {/* Output summary */}
                    {step.output_summary && (
                      <div className="bg-[#09090b] p-2 rounded border border-zinc-800 text-[11px] text-zinc-300">
                        <span className="text-[9px] text-zinc-500 uppercase font-bold block mb-0.5">Output</span>
                        {step.output_summary}
                      </div>
                    )}

                    {/* Tool used / Knowledge retrieval info */}
                    {step.tool_used && (
                      <div className="flex items-center gap-1.5 text-[10px] text-zinc-400">
                        <Wrench className="h-3 w-3 text-amber-400" />
                        <span>Tool Invoked: <strong className="text-zinc-200">{step.tool_used}</strong></span>
                      </div>
                    )}

                    {step.error && (
                      <div className="bg-rose-950/40 border border-rose-800/60 p-2 rounded text-[11px] text-rose-300">
                        <span className="font-bold">Error:</span> {step.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-zinc-500 text-xs">No execution details available</div>
        )}
      </DetailDrawer>
    </div>
  );
}
