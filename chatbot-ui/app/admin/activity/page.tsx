'use client';

import { useState, useEffect } from 'react';
import { fetchActivity } from '@/lib/api-client';
import { Search, RotateCw, Activity, Shield, Cpu, Mail as MailIcon } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

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
        limit: 100,
      });
      setActivities(result.activities || []);
      setError(null);
    } catch (err) {
      setError('Failed to load activity log');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">Activity Log</h1>
          <p className="text-xs text-zinc-400">System events, agent dispatches & audit trail</p>
        </div>
        <button
          onClick={loadActivities}
          className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
        >
          <RotateCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Tabs & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center bg-[#111113] border border-zinc-800 p-1 rounded-xl gap-1">
          {['all', 'system', 'agent', 'email', 'security'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all',
                activeTab === tab
                  ? 'bg-zinc-800 text-zinc-50 border border-zinc-700/60'
                  : 'text-zinc-400 hover:text-zinc-200'
              )}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search activity events..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#111113] border border-zinc-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
          />
        </div>
      </div>

      {/* Activity List */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-400 animate-pulse">Loading activity logs...</div>
        ) : error ? (
          <div className="py-8 text-center text-rose-400 text-xs">{error}</div>
        ) : activities.length === 0 ? (
          <div className="py-12 text-center text-zinc-500 text-xs">No activity logs recorded for this view</div>
        ) : (
          <div className="space-y-2">
            {activities.map((act) => (
              <div
                key={act.id}
                className="bg-[#09090b] border border-zinc-800/80 rounded-lg p-3 flex items-start gap-3 text-xs hover:border-zinc-700/80 transition-colors"
              >
                <div
                  className={cn(
                    'mt-1 h-2 w-2 rounded-full flex-shrink-0',
                    act.level === 'error' || act.level === 'critical'
                      ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]'
                      : act.level === 'warning'
                      ? 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]'
                      : 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]'
                  )}
                />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[9px] font-bold font-mono uppercase bg-zinc-900 border border-zinc-800 px-1.5 py-0.2 rounded text-zinc-300">
                      {act.type || 'system'}
                    </span>
                    <span className="text-[10px] text-zinc-500">
                      {act.timestamp
                        ? formatDistanceToNow(new Date(act.timestamp), { addSuffix: true })
                        : 'Recently'}
                    </span>
                  </div>
                  <p className="text-zinc-200 font-medium leading-relaxed">{act.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
