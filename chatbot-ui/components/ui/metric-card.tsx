import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'stable';
  description?: string;
  icon?: React.ReactNode;
}

export function MetricCard({ title, value, change, trend, description, icon }: MetricCardProps) {
  const trendIcon = {
    up: TrendingUp,
    down: TrendingDown,
    stable: Minus,
  };

  const trendColor = {
    up: 'text-green-500',
    down: 'text-red-500',
    stable: 'text-muted-foreground',
  };

  const TrendIcon = trend ? trendIcon[trend] : null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {(change !== undefined || description) && (
          <div className="flex items-center gap-2 mt-2">
            {change !== undefined && TrendIcon && (
              <div className={cn('flex items-center gap-1 text-xs', trend && trendColor[trend])}>
                <TrendIcon className="size-3" />
                <span>{Math.abs(change)}%</span>
              </div>
            )}
            {description && (
              <p className="text-xs text-muted-foreground">{description}</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
