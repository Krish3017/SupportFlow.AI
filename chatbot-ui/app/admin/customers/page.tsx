'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { CustomerCard } from '@/components/dashboard/customer-card';
import { LoadingState } from '@/components/ui/loading-state';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { fetchCustomers, fetchCustomerDetail } from '@/lib/api-client';
import { Search } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);

  useEffect(() => {
    loadCustomers();
  }, [searchQuery]);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const result = await fetchCustomers({
        search: searchQuery || undefined,
        limit: 50
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
      const detail = await fetchCustomerDetail(id);
      setSelectedCustomer(detail);
    } catch (err) {
      console.error('Failed to load customer detail:', err);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 60) return 'text-red-500';
    if (score >= 30) return 'text-amber-500';
    return 'text-green-500';
  };

  const getTierVariant = (tier: string) => {
    if (tier === 'vip') return 'bg-purple-500/10 text-purple-500 ring-1 ring-purple-500/20';
    if (tier === 'new') return 'bg-green-500/10 text-green-500 ring-1 ring-green-500/20';
    return 'bg-blue-500/10 text-blue-500 ring-1 ring-blue-500/20';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Customers</h1>
        <p className="text-muted-foreground">Customer directory and intelligence</p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search customers..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      {loading ? (
        <LoadingState message="Loading customers..." />
      ) : error ? (
        <Card className="p-8 text-center text-red-500">{error}</Card>
      ) : customers.length === 0 ? (
        <Card className="p-8 text-center text-muted-foreground">
          No customers found
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {customers.map((customer) => (
            <Card
              key={customer.id}
              className="p-4 cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => selectCustomer(customer.id)}
            >
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm truncate">
                      {customer.name || customer.email}
                    </h4>
                    <p className="text-xs text-muted-foreground truncate">{customer.email}</p>
                  </div>
                  <Badge variant="outline" className={getTierVariant(customer.tier)}>
                    {customer.tier}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <p className="text-muted-foreground">Tickets</p>
                    <p className="font-semibold">
                      {customer.resolved_tickets}/{customer.total_tickets}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Risk Score</p>
                    <p className={`font-semibold ${getRiskColor(customer.risk_score)}`}>
                      {customer.risk_score}%
                    </p>
                  </div>
                </div>

                {customer.last_interaction && (
                  <div className="pt-2 border-t">
                    <p className="text-xs text-muted-foreground">
                      Last seen {formatDistanceToNow(new Date(customer.last_interaction), { addSuffix: true })}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {selectedCustomer && (
        <Card className="p-6 mt-6 border-2">
          <div className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-semibold">{selectedCustomer.name || selectedCustomer.email}</h3>
                <Badge variant="outline" className={getTierVariant(selectedCustomer.tier)}>
                  {selectedCustomer.tier}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{selectedCustomer.email}</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Tickets</p>
                <p className="text-2xl font-bold">{selectedCustomer.total_tickets}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Resolved</p>
                <p className="text-2xl font-bold text-green-500">{selectedCustomer.resolved_tickets}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Open</p>
                <p className="text-2xl font-bold text-blue-500">{selectedCustomer.open_tickets}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Risk Score</p>
                <p className={`text-2xl font-bold ${getRiskColor(selectedCustomer.risk_score)}`}>
                  {selectedCustomer.risk_score}%
                </p>
              </div>
            </div>

            {selectedCustomer.tickets && selectedCustomer.tickets.length > 0 && (
              <div>
                <h4 className="font-semibold mb-3">Recent Tickets</h4>
                <div className="space-y-2">
                  {selectedCustomer.tickets.slice(0, 5).map((ticket: any) => (
                    <div key={ticket.id} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{ticket.subject}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(ticket.created_at), { addSuffix: true })}
                        </p>
                      </div>
                      <Badge variant="outline">{ticket.status}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
