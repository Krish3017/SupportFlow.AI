import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { Agent } from '@/lib/mock-data';
import { CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

interface AgentHealthCardProps {
  agent: Agent;
  onClick?: () => void;
}

export function AgentHealthCard({ agent, onClick }: AgentHealthCardProps) {
  const statusConfig = {
    healthy: {
      icon: CheckCircle2,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
      label: 'Healthy',
    },
    degraded: {
      icon: AlertCircle,
      color: 'text-amber-500',
      bgColor: 'bg-amber-500/10',
      label: 'Degraded',
    },
    offline: {
      icon: XCircle,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
      label: 'Offline',
    },
  };

  const { icon: StatusIcon, color, bgColor, label } = statusConfig[agent.status];

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:shadow-md hover:ring-1 hover:ring-ring',
        agent.status === 'degraded' && 'ring-1 ring-amber-500/20'
      )}
      onClick={onClick}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{agent.name}</CardTitle>
        <div className={cn('rounded-full p-1', bgColor)}>
          <StatusIcon className={cn('size-4', color)} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Status</span>
            <Badge variant="outline" className={cn(bgColor, color, 'ring-0')}>
              {label}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Success Rate</span>
            <span className="text-sm font-semibold">{agent.successRate}%</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Avg Latency</span>
            <span className="text-sm font-semibold">{agent.avgLatency}s</span>
          </div>
          {agent.lastError && (
            <div className="pt-2 border-t">
              <p className="text-xs text-red-500 truncate" title={agent.lastError}>
                {agent.lastError}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
