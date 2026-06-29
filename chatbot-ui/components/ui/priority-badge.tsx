import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { Priority } from '@/lib/mock-data';
import { AlertCircle, ChevronUp, Minus, ChevronDown } from 'lucide-react';

interface PriorityBadgeProps {
  priority: Priority;
  showIcon?: boolean;
  className?: string;
}

export function PriorityBadge({ priority, showIcon = true, className }: PriorityBadgeProps) {
  const config = {
    critical: {
      variant: 'bg-red-600 text-white ring-0',
      label: 'Critical',
      icon: AlertCircle,
    },
    high: {
      variant: 'bg-amber-500/10 text-amber-500 ring-1 ring-amber-500/20',
      label: 'High',
      icon: ChevronUp,
    },
    medium: {
      variant: 'bg-blue-500/10 text-blue-500 ring-1 ring-blue-500/20',
      label: 'Medium',
      icon: Minus,
    },
    low: {
      variant: 'bg-muted-foreground/10 text-muted-foreground ring-1 ring-muted-foreground/20',
      label: 'Low',
      icon: ChevronDown,
    },
  };

  const { variant, label, icon: Icon } = config[priority];

  return (
    <Badge variant="outline" className={cn(variant, 'gap-1', className)}>
      {showIcon && <Icon className="size-3" />}
      {label}
    </Badge>
  );
}
