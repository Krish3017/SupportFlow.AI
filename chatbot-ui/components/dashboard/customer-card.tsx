import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { SentimentIcon } from '@/components/ui/sentiment-icon';
import { formatDistanceToNow } from 'date-fns';
import type { Customer } from '@/lib/mock-data';
import { cn } from '@/lib/utils';

interface CustomerCardProps {
  customer: Customer;
  onClick?: () => void;
}

export function CustomerCard({ customer, onClick }: CustomerCardProps) {
  const tierConfig = {
    vip: { label: 'VIP', variant: 'bg-purple-500/10 text-purple-500 ring-1 ring-purple-500/20' },
    standard: {
      label: 'Standard',
      variant: 'bg-blue-500/10 text-blue-500 ring-1 ring-blue-500/20',
    },
    new: { label: 'New', variant: 'bg-green-500/10 text-green-500 ring-1 ring-green-500/20' },
  };

  const tierInfo = tierConfig[customer.tier];

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRiskColor = (score: number) => {
    if (score >= 60) return 'text-red-500';
    if (score >= 30) return 'text-amber-500';
    return 'text-green-500';
  };

  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-md hover:ring-1 hover:ring-ring"
      onClick={onClick}
    >
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start gap-3">
          <Avatar className="size-10">
            <AvatarFallback>{getInitials(customer.name)}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm truncate">{customer.name}</h4>
            <p className="text-xs text-muted-foreground truncate">{customer.email}</p>
          </div>
          <Badge variant="outline" className={cn(tierInfo.variant, 'text-xs')}>
            {tierInfo.label}
          </Badge>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <p className="text-muted-foreground">Tickets</p>
            <p className="font-semibold">
              {customer.resolvedTickets}/{customer.totalTickets}
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Avg Response</p>
            <p className="font-semibold">{customer.avgResponseTime.toFixed(1)}m</p>
          </div>
          <div>
            <p className="text-muted-foreground">Risk Score</p>
            <p className={cn('font-semibold', getRiskColor(customer.riskScore))}>
              {customer.riskScore}%
            </p>
          </div>
          <div className="flex items-center gap-1">
            <p className="text-muted-foreground">Sentiment</p>
            <SentimentIcon sentiment={customer.sentiment} />
          </div>
        </div>

        <div className="pt-2 border-t">
          <p className="text-xs text-muted-foreground">
            Last seen {formatDistanceToNow(customer.lastInteraction, { addSuffix: true })}
          </p>
        </div>

        {customer.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {customer.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
