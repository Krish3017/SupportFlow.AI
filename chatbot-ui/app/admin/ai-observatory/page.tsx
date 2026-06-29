'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/ui/loading-state';
import { fetchAgentHealth, fetchExecutions, fetchExecutionDetail } from '@/lib/api-client';
import { CheckCircle2, XCircle, AlertCircle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function AIObservatoryPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [agentResult, execResult] = await Promise.all([
        fetchAgentHealth(),
        fetchExecutions({ limit: 20 })
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
      const detail = await fetchExecutionDetail(id);
      setSelectedExecution(detail);
    } catch (err) {
      console.error('Failed to load execution detail:', err);
    }
  };

  const statusConfig = {
    healthy: { icon: CheckCircle2, color: 'text-green-500', bgColor: 'bg-green-500/10' },
    degraded: { icon: AlertCircle, color: 'text-amber-500', bgColor: 'bg-amber-500/10' },
    offline: { icon: XCircle, color: 'text-red-500', bgColor: 'bg-red-500/10' },
  };

  if (loading) return <LoadingState message="Loading AI Observatory..." />;
  if (error) return <Card className="p-8 text-center text-red-500">{error}</Card>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Observatory</h1>
        <p className="text-muted-foreground">Monitor agent performance and workflows</p>
      </div>

      {/* Agent Health Grid */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Agent Health</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => {
            const config = statusConfig[agent.status as keyof typeof statusConfig] || statusConfig.healthy;
            const StatusIcon = config.icon;

            return (
              <Card key={agent.id} className={cn(
                'transition-all hover:shadow-md',
                agent.status === 'degraded' && 'ring-1 ring-amber-500/20'
              )}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{agent.name}</CardTitle>
                  <div className={cn('rounded-full p-1', config.bgColor)}>
                    <StatusIcon className={cn('size-4', config.color)} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Status</span>
                      <Badge variant="outline" className={cn(config.bgColor, config.color, 'ring-0')}>
                        {agent.status}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Success Rate</span>
                      <span className="text-sm font-semibold">
                        {agent.total_executions > 0
                          ? `${((agent.successful_executions / agent.total_executions) * 100).toFixed(1)}%`
                          : 'N/A'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Avg Latency</span>
                      <span className="text-sm font-semibold">{agent.avg_latency}s</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Executions</span>
                      <span className="text-sm font-semibold">{agent.total_executions}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Executions */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Executions</h2>
        {executions.length === 0 ? (
          <Card className="p-8 text-center text-muted-foreground">
            No executions recorded yet
          </Card>
        ) : (
          <div className="space-y-3">
            {executions.map((exec) => (
              <Card
                key={exec.id}
                className="p-4 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => selectExecution(exec.id)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-medium">Ticket #{exec.ticket_id}</span>
                    <span className="text-muted-foreground text-sm ml-2">
                      {exec.step_count} steps
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={
                      exec.status === 'success' ? 'bg-green-500/10 text-green-500' :
                      exec.status === 'failed' ? 'bg-red-500/10 text-red-500' :
                      'bg-blue-500/10 text-blue-500'
                    }>
                      {exec.status}
                    </Badge>
                    <span className="text-sm text-muted-foreground">{exec.total_duration}s</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Execution Detail Timeline */}
      {selectedExecution && (
        <Card className="p-6 border-2">
          <CardHeader className="px-0 pt-0">
            <CardTitle>Execution Timeline (Ticket #{selectedExecution.ticket_id})</CardTitle>
          </CardHeader>
          <CardContent className="px-0 pb-0">
            <div className="space-y-4">
              {selectedExecution.steps?.map((step: any, index: number) => (
                <div key={index} className="flex items-start gap-4">
                  <div className="flex flex-col items-center gap-2">
                    <div className={cn('rounded-full p-1',
                      step.status === 'success' ? 'bg-green-500/10' :
                      step.status === 'failed' ? 'bg-red-500/10' :
                      'bg-blue-500/10'
                    )}>
                      {step.status === 'success' && <CheckCircle2 className="size-4 text-green-500" />}
                      {step.status === 'failed' && <XCircle className="size-4 text-red-500" />}
                      {step.status === 'running' && <Clock className="size-4 text-blue-500 animate-pulse" />}
                    </div>
                    {index < selectedExecution.steps.length - 1 && (
                      <div className="h-8 w-px bg-border" />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-sm">{step.agent_name}</h4>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">{step.duration}s</Badge>
                      </div>
                    </div>
                    {step.input_summary && (
                      <p className="text-sm text-muted-foreground mb-1">
                        Input: {step.input_summary}
                      </p>
                    )}
                    {step.output_summary && (
                      <p className="text-sm text-muted-foreground">
                        Output: {step.output_summary}
                      </p>
                    )}
                    {step.error && (
                      <p className="text-sm text-red-500">Error: {step.error}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
