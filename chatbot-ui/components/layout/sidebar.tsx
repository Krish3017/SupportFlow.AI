'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  LayoutDashboard,
  MessageSquare,
  Ticket,
  Users,
  Microscope,
  BookOpen,
  BarChart3,
  Activity,
  Settings,
  Mail,
} from 'lucide-react';

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
  badgeVariant?: 'default' | 'destructive' | 'warning';
  separator?: boolean;
}

const navItems: NavItem[] = [
  {
    title: 'Overview',
    href: '/admin',
    icon: LayoutDashboard,
  },
  {
    title: 'Conversations',
    href: '/admin/conversations',
    icon: MessageSquare,
    separator: true,
  },
  {
    title: 'Tickets',
    href: '/admin/tickets',
    icon: Ticket,
    badge: 23,
  },
  {
    title: 'Customers',
    href: '/admin/customers',
    icon: Users,
    separator: true,
  },
  {
    title: 'AI Observatory',
    href: '/admin/ai-observatory',
    icon: Microscope,
    badge: 2,
    badgeVariant: 'destructive',
  },
  {
    title: 'Knowledge Base',
    href: '/admin/knowledge',
    icon: BookOpen,
    separator: true,
  },
  {
    title: 'Email Center',
    href: '/admin/email',
    icon: Mail,
    separator: true,
  },
  {
    title: 'Analytics',
    href: '/admin/analytics',
    icon: BarChart3,
  },
  {
    title: 'Activity',
    href: '/admin/activity',
    icon: Activity,
    separator: true,
  },
  {
    title: 'Settings',
    href: '/admin/settings',
    icon: Settings,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  const getBadgeVariant = (variant?: 'default' | 'destructive' | 'warning') => {
    if (variant === 'destructive') return 'bg-red-500 text-white';
    if (variant === 'warning') return 'bg-amber-500 text-white';
    return 'bg-primary text-primary-foreground';
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r bg-sidebar">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-14 items-center border-b px-6">
          <Link href="/admin" className="flex items-center gap-2 font-semibold">
            <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <span className="text-sm font-bold">SF</span>
            </div>
            <span className="text-sm">SupportFlow AI</span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
              const Icon = item.icon;

              return (
                <li key={item.href}>
                  <Link href={item.href}>
                    <Button
                      variant={isActive ? 'secondary' : 'ghost'}
                      className={cn(
                        'w-full justify-start gap-3',
                        isActive && 'bg-sidebar-accent text-sidebar-accent-foreground'
                      )}
                    >
                      <Icon className="size-4" />
                      <span className="flex-1 text-left">{item.title}</span>
                      {item.badge !== undefined && (
                        <Badge
                          variant="outline"
                          className={cn('h-5 px-1.5 text-xs', getBadgeVariant(item.badgeVariant))}
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </Button>
                  </Link>
                  {item.separator && <div className="my-2 border-t" />}
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
    </aside>
  );
}
