import { Card, CardContent } from '@/components/ui/card';
import { PriorityBadge } from '@/components/ui/priority-badge';
import { StatusBadge } from '@/components/ui/status-badge';
import { SentimentIcon } from '@/components/ui/sentiment-icon';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import type { Ticket } from '@/lib/mock-data';
import { Mail, MessageSquare, Send } from 'lucide-react';

interface TicketCardProps {
  ticket: Ticket;
  onClick?: () => void;
}

export function TicketCard({ ticket, onClick }: TicketCardProps) {
  const channelIcons = {
    email: Mail,
    chat: MessageSquare,
    telegram: Send,
  };

  const ChannelIcon = channelIcons[ticket.channel];

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-md hover:ring-1 hover:ring-ring"
      onClick={onClick}
    >
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <PriorityBadge priority={ticket.priority} />
          <StatusBadge status={ticket.status} />
        </div>

        <div>
          <h4 className="font-medium text-sm mb-1 line-clamp-2">{ticket.subject}</h4>
          <p className="text-xs text-muted-foreground">#{ticket.id}</p>
        </div>

        <div className="flex items-center gap-2">
          <Avatar className="size-6">
            <AvatarFallback className="text-xs">
              {getInitials(ticket.customer.name)}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium truncate">{ticket.customer.name}</p>
            <p className="text-xs text-muted-foreground truncate">{ticket.customer.email}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-2">
            <ChannelIcon className="size-3 text-muted-foreground" />
            <span className="text-xs text-muted-foreground capitalize">{ticket.channel}</span>
            <span className="text-xs text-muted-foreground">•</span>
            <span className="text-xs text-muted-foreground">
              {formatDistanceToNow(ticket.createdAt, { addSuffix: true })}
            </span>
          </div>
          <SentimentIcon sentiment={ticket.sentiment} />
        </div>

        {ticket.currentAgent && (
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {ticket.currentAgent.replace('_', ' ')}
            </Badge>
            <span className="text-xs text-muted-foreground">{ticket.timeElapsed}s</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
