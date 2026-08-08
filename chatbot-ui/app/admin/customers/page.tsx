'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DetailDrawer } from '@/components/ui/detail-drawer';
import { fetchCustomers, fetchCustomerDetail } from '@/lib/api-client';
import { Search, RotateCw, UserCheck, ShieldAlert, ChevronRight } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, [searchQuery]);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const result = await fetchCustomers({
        search: searchQuery || undefined,
        limit: 50,
      });
      setCustomers(result.customers || []);
      setError(null);
    } catch (err) {
      setError('Failed to load customers');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectCustomer = async (id: string) => {
    try {
      setDrawerLoading(true);
      setIsDrawerOpen(true);
      const detail = await fetchCustomerDetail(id);
      setSelectedCustomer(detail);
    } catch (err) {
      console.error('Failed to load customer detail:', err);
    } finally {
      setDrawerLoading(false);
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'vip':
      case 'platinum':
        return 'bg-purple-950/80 text-purple-300 border-purple-800/60';
      case 'gold':
        return 'bg-amber-950/80 text-amber-300 border-amber-800/60';
      default:
        return 'bg-zinc-900 text-zinc-300 border-zinc-800';
    }
  };

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">Customer Directory</h1>
          <p className="text-xs text-zinc-400">Customer intelligence, tiers & risk assessment</p>
        </div>
        <button
          onClick={loadCustomers}
          className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
        >
          <RotateCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
        <input
          type="text"
          placeholder="Search customer email, name or ID..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-[#111113] border border-zinc-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
        />
      </div>

      {/* Customer Grid */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-400 animate-pulse">Loading customer profiles...</div>
        ) : error ? (
          <div className="py-8 text-center text-rose-400 text-xs">{error}</div>
        ) : customers.length === 0 ? (
          <div className="py-12 text-center text-zinc-500 text-xs">No customer profiles found</div>
        ) : (
          <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {customers.map((c) => (
              <div
                key={c.id}
                onClick={() => selectCustomer(c.id)}
                className="bg-[#09090b] border border-zinc-800/80 hover:border-zinc-700/80 rounded-xl p-3.5 cursor-pointer transition-all hover:scale-[1.01] flex flex-col justify-between"
              >
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <h4 className="text-xs font-bold text-zinc-100 truncate">{c.name || c.email}</h4>
                    <p className="text-[11px] text-zinc-400 truncate">{c.email}</p>
                  </div>
                  <span className={cn('text-[9px] font-bold px-2 py-0.5 rounded-full border uppercase ml-2', getTierColor(c.tier))}>
                    {c.tier || 'standard'}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[10px] my-3 p-2 bg-[#111113] border border-zinc-800/60 rounded-lg">
                  <div>
                    <span className="text-zinc-500 block">Total Tickets</span>
                    <span className="font-bold text-zinc-200">{c.total_tickets || 0}</span>
                  </div>
                  <div>
                    <span className="text-zinc-500 block">Resolved</span>
                    <span className="font-bold text-emerald-400">{c.resolved_tickets || 0}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[10px] text-zinc-500 pt-1 border-t border-zinc-800/60">
                  <span>ID: {c.company_customer_id || c.id}</span>
                  <ChevronRight className="h-3.5 w-3.5 text-zinc-500" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Customer Detail Side Drawer */}
      <DetailDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        title={selectedCustomer ? `Customer Intelligence Profile` : 'Customer Profile'}
        subtitle={selectedCustomer?.email || 'Loading customer details...'}
        widthClass="max-w-xl"
      >
        {drawerLoading ? (
          <div className="py-12 text-center text-zinc-400 text-xs animate-pulse">Loading profile data...</div>
        ) : selectedCustomer ? (
          <div className="space-y-4">
            <div className="p-3 bg-[#111113] border border-zinc-800 rounded-lg text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-zinc-500">Name:</span>
                <span className="font-semibold text-zinc-100">{selectedCustomer.name || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Email:</span>
                <span className="font-mono text-zinc-200">{selectedCustomer.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Tier:</span>
                <span className={cn('px-2 py-0.5 rounded-full border text-[9px] font-bold uppercase', getTierColor(selectedCustomer.tier))}>
                  {selectedCustomer.tier || 'standard'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-3 bg-[#111113] border border-zinc-800 rounded-lg">
                <span className="text-[10px] text-zinc-500 uppercase font-bold block">Total Support Tickets</span>
                <span className="text-lg font-black text-zinc-100 mt-1 block">{selectedCustomer.total_tickets || 0}</span>
              </div>
              <div className="p-3 bg-[#111113] border border-zinc-800 rounded-lg">
                <span className="text-[10px] text-zinc-500 uppercase font-bold block">Resolved Ratio</span>
                <span className="text-lg font-black text-emerald-400 mt-1 block">
                  {selectedCustomer.resolved_tickets || 0} / {selectedCustomer.total_tickets || 0}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-zinc-500 text-xs">No customer profile details available</div>
        )}
      </DetailDrawer>
    </div>
  );
}
