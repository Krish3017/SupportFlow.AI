'use client';

import { useState, useEffect } from 'react';
import { MetricCard } from '@/components/ui/metric-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LoadingState } from '@/components/ui/loading-state';
import { fetchAnalyticsOverview, fetchAgentHealth, fetchActivity } from '@/lib/api-client';
import { formatDistanceToNow } from 'date-fns';
import { Activity, Ticket, Clock, TrendingUp, AlertCircle, ArrowRight, CheckCircle2, XCircle } from 'lucide-react';
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
        fetchActivity({ limit: 8 })
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

  if (loading) return <LoadingState message="Loading dashboard..." />;
  if (error) return <Card className="p-8 text-center text-red-500">{error}</Card>;

  const statusConfig: Record<string, { icon: any; color: string; bgColor: string }> = {
    healthy: { icon: CheckCircle2, color: 'text-green-500', bgColor: 'bg-green-500/10' },
    degraded: { icon: AlertCircle, color: 'text-amber-500', bgColor: 'bg-amber-500/10' },
    offline: { icon: XCircle, color: 'text-red-500', bgColor: 'bg-red-500/10' },
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
        <p className="text-muted-foreground">AI Operations Center</p>
      </div>

      {/* Agent Health */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Agent Health</h2>
          <Link href="/admin/ai-observatory">
            <Button variant="ghost" size="sm">
              View Details <ArrowRight className="ml-2 size-4" />
            </Button>
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          {agents.map((agent) => {
            const config = statusConfig[agent.status] || statusConfig.healthy;
            const StatusIcon = config.icon;
            return (
              <Card key={agent.id}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-xs font-medium truncate">{agent.name}</CardTitle>
                  <div className={cn('rounded-full p-1', config.bgColor)}>
                    <StatusIcon className={cn('size-3', config.color)} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-lg font-bold">
                    {agent.total_executions > 0
                      ? `${((agent.successful_executions / agent.total_executions) * 100).toFixed(0)}%`
                      : 'N/A'}
                  </div>
                  <p className="text-xs text-muted-foreground">{agent.avg_latency}s avg</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Metrics */}
      {overview && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Tickets"
            value={overview.tickets.total}
            description={`${overview.tickets.open} open`}
            icon={<Ticket className="size-4" />}
          />
          <MetricCard
            title="Resolved"
            value={overview.tickets.resolved}
            description="total resolved"
            icon={<CheckCircle2 className="size-4" />}
          />
          <MetricCard
            title="Escalated"
            value={overview.tickets.escalated}
            description="needs human"
            icon={<AlertCircle className="size-4" />}
          />
          <MetricCard
            title="AI Success Rate"
            value={`${overview.agents.success_rate}%`}
            description={`${overview.agents.total_executions} executions`}
            icon={<TrendingUp className="size-4" />}
          />
        </div>
      )}

      {/* Activity Feed */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Activity</CardTitle>
          <Link href="/admin/activity">
            <Button variant="ghost" size="sm">View All</Button>
          </Link>
        </CardHeader>
        <CardContent>
          {activity.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">No activity yet</p>
          ) : (
            <div className="space-y-3">
              {activity.map((item) => (
                <div key={item.id} className="flex items-start gap-3 text-sm">
                  <div className={`mt-1 size-2 rounded-full flex-shrink-0 ${
                    item.level === 'error' || item.level === 'critical'
                      ? 'bg-red-500'
                      : item.level === 'warning'
                        ? 'bg-amber-500'
                        : 'bg-green-500'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="line-clamp-2">{item.message}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })}
                    </p>
                  </div>
                  <Badge variant="outline" className="text-xs capitalize flex-shrink-0">
                    {item.type}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
