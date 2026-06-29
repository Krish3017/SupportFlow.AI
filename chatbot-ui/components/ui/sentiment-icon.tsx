import { cn } from '@/lib/utils';
import type { Sentiment } from '@/lib/mock-data';
import { Smile, Meh, Frown } from 'lucide-react';

interface SentimentIconProps {
  sentiment: Sentiment;
  className?: string;
}

export function SentimentIcon({ sentiment, className }: SentimentIconProps) {
  const config = {
    positive: {
      icon: Smile,
      color: 'text-green-500',
    },
    neutral: {
      icon: Meh,
      color: 'text-muted-foreground',
    },
    negative: {
      icon: Frown,
      color: 'text-red-500',
    },
  };

  const { icon: Icon, color } = config[sentiment];

  return <Icon className={cn('size-4', color, className)} />;
}
