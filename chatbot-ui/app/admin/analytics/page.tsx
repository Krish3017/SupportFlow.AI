'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoadingState } from '@/components/ui/loading-state';
import { fetchAnalyticsOverview, fetchTicketAnalytics, fetchAgentAnalytics } from '@/lib/api-client';
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

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewRes, ticketRes, agentRes] = await Promise.all([
        fetchAnalyticsOverview(),
        fetchTicketAnalytics(),
        fetchAgentAnalytics()
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

  if (loading) return <LoadingState message="Loading analytics..." />;
  if (error) return <Card className="p-8 text-center text-red-500">{error}</Card>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">Performance insights and trends</p>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Total Tickets</p>
              <p className="text-2xl font-bold">{overview.tickets.total}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Resolved</p>
              <p className="text-2xl font-bold text-green-500">{overview.tickets.resolved}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Escalated</p>
              <p className="text-2xl font-bold text-red-500">{overview.tickets.escalated}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">AI Success Rate</p>
              <p className="text-2xl font-bold">{overview.agents.success_rate}%</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Customers</p>
              <p className="text-2xl font-bold">{overview.customers.total}</p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="support">
        <TabsList>
          <TabsTrigger value="support">Support</TabsTrigger>
          <TabsTrigger value="ai">AI Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="support" className="space-y-6">
          {ticketAnalytics && (
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Tickets by Priority</CardTitle>
                </CardHeader>
                <CardContent>
                  {ticketAnalytics.by_priority.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={ticketAnalytics.by_priority}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="priority" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#6366f1" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">No data yet</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Tickets by Channel</CardTitle>
                </CardHeader>
                <CardContent>
                  {ticketAnalytics.by_channel.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={ticketAnalytics.by_channel}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="channel" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#10b981" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">No data yet</p>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="ai" className="space-y-6">
          {agentAnalytics && (
            <Card>
              <CardHeader>
                <CardTitle>Agent Performance</CardTitle>
              </CardHeader>
              <CardContent>
                {agentAnalytics.by_agent.length > 0 ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={agentAnalytics.by_agent}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="agent_name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="success" fill="#10b981" name="Success" />
                      <Bar dataKey="failed" fill="#ef4444" name="Failed" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No execution data yet</p>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
