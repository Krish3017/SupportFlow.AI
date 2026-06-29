'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { LoadingState } from '@/components/ui/loading-state';
import { fetchActivity } from '@/lib/api-client';
import { Search } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function ActivityPage() {
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadActivities();
  }, [activeTab, searchQuery]);

  const loadActivities = async () => {
    try {
      setLoading(true);
      const result = await fetchActivity({
        type: activeTab === 'all' ? undefined : activeTab,
        search: searchQuery || undefined,
        limit: 100
      });
      setActivities(result.activities || []);
      setError(null);
    } catch (err) {
      setError('Failed to load activity');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error':
      case 'critical':
        return 'bg-red-500';
      case 'warning':
        return 'bg-amber-500';
      default:
        return 'bg-green-500';
    }
  };

  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'error':
      case 'critical':
        return 'bg-red-500/10 text-red-500';
      case 'warning':
        return 'bg-amber-500/10 text-amber-500';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Activity</h1>
        <p className="text-muted-foreground">System activity and event logs</p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search activity..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
          <TabsTrigger value="agent">Agents</TabsTrigger>
          <TabsTrigger value="email">Emails</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab}>
          {loading ? (
            <LoadingState message="Loading activity..." />
          ) : error ? (
            <Card className="p-8 text-center text-red-500">{error}</Card>
          ) : activities.length === 0 ? (
            <Card className="p-8 text-center text-muted-foreground">
              No activity found
            </Card>
          ) : (
            <div className="space-y-3">
              {activities.map((activity) => (
                <Card key={activity.id} className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 size-2 rounded-full flex-shrink-0 ${getLevelColor(activity.level)}`} />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="text-xs capitalize">
                          {activity.type}
                        </Badge>
                        <Badge variant="outline" className={`text-xs ${getLevelBadge(activity.level)}`}>
                          {activity.level}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                        </span>
                      </div>
                      <p className="text-sm">{activity.message}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
