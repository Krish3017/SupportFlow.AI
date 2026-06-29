import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { Status } from '@/lib/mock-data';

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const variants = {
    new: 'bg-blue-500/10 text-blue-500 ring-1 ring-blue-500/20',
    in_progress: 'bg-amber-500/10 text-amber-500 ring-1 ring-amber-500/20',
    resolved: 'bg-green-500/10 text-green-500 ring-1 ring-green-500/20',
    escalated: 'bg-red-500/10 text-red-500 ring-1 ring-red-500/20',
  };

  const labels = {
    new: 'New',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    escalated: 'Escalated',
  };

  return (
    <Badge variant="outline" className={cn(variants[status], className)}>
      {labels[status]}
    </Badge>
  );
}
