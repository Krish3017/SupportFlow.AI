'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
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
  HelpCircle,
  Sparkles,
} from 'lucide-react';

interface NavGroup {
  groupName: string;
  items: {
    name: string;
    href: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: string | number;
    badgeColor?: string;
  }[];
}

const navGroups: NavGroup[] = [
  {
    groupName: 'OPERATIONS',
    items: [
      { name: 'Overview', href: '/admin', icon: LayoutDashboard },
      { name: 'Conversations', href: '/admin/conversations', icon: MessageSquare },
      { name: 'Tickets', href: '/admin/tickets', icon: Ticket, badge: 'Live' },
      { name: 'Customers', href: '/admin/customers', icon: Users },
    ],
  },
  {
    groupName: 'AI ENGINE',
    items: [
      { name: 'AI Observatory', href: '/admin/ai-observatory', icon: Microscope, badge: '6 Agents', badgeColor: 'bg-emerald-950/90 text-emerald-300 border-emerald-700/80 font-bold' },
      { name: 'Knowledge Base', href: '/admin/knowledge', icon: BookOpen },
    ],
  },
  {
    groupName: 'COMMUNICATION',
    items: [
      { name: 'Email Center', href: '/admin/email', icon: Mail },
    ],
  },
  {
    groupName: 'INSIGHTS & SYSTEM',
    items: [
      { name: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
      { name: 'Activity Log', href: '/admin/activity', icon: Activity },
      { name: 'Settings', href: '/admin/settings', icon: Settings },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 bg-[#09090b] border-r border-zinc-800/80 p-3.5 flex flex-col justify-between flex-shrink-0 h-screen fixed left-0 top-0 z-30 select-none">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-2.5 px-2 py-2 mb-4 border-b border-zinc-800/70">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-zinc-950 font-bold text-sm shadow-[0_0_14px_rgba(52,211,153,0.35)]">
            <Sparkles className="h-4.5 w-4.5 fill-zinc-950" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-bold text-zinc-100 tracking-tight">SupportFlow AI</span>
            <span className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider">Multi-Agent System</span>
          </div>
        </div>

        {/* Grouped Navigation */}
        <nav className="space-y-4">
          {navGroups.map((group) => (
            <div key={group.groupName}>
              <div className="text-[10px] font-extrabold text-zinc-400 uppercase tracking-widest mb-1.5 px-2.5">
                {group.groupName}
              </div>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive =
                    item.href === '/admin'
                      ? pathname === '/admin'
                      : pathname?.startsWith(item.href);

                  return (
                    <Link key={item.href} href={item.href}>
                      <button
                        className={cn(
                          'w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition-all group',
                          isActive
                            ? 'bg-zinc-800/90 text-zinc-50 font-bold border border-zinc-700/60 shadow-sm'
                            : 'text-zinc-300 hover:text-zinc-100 hover:bg-zinc-800/50'
                        )}
                      >
                        <div className="flex items-center gap-2.5">
                          <Icon
                            className={cn(
                              'h-4 w-4 transition-colors',
                              isActive ? 'text-emerald-400' : 'text-zinc-400 group-hover:text-zinc-200'
                            )}
                          />
                          <span className="text-xs">{item.name}</span>
                        </div>

                        {item.badge !== undefined && (
                          <span
                            className={cn(
                              'text-[10px] font-bold px-2 py-0.5 rounded-full border',
                              item.badgeColor || 'bg-zinc-800/90 text-zinc-200 border-zinc-700/60'
                            )}
                          >
                            {item.badge}
                          </span>
                        )}
                      </button>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </div>

      {/* Footer Info Box */}
      <div className="space-y-2.5 pt-3 border-t border-zinc-800/80">
        <div className="p-2.5 rounded-lg bg-[#111113] border border-zinc-800 text-xs">
          <div className="text-[10px] text-emerald-400 uppercase tracking-wider font-bold">
            System Online
          </div>
          <div className="font-bold text-zinc-100 mt-0.5 text-xs">FastAPI & LangGraph</div>
          <div className="text-[10px] text-zinc-300 font-medium">Groq LLM Active</div>
        </div>

        <div className="flex items-center justify-between text-xs text-zinc-400 px-1 font-medium">
          <Link href="/chat" className="flex items-center gap-1.5 hover:text-zinc-100 transition-colors">
            <HelpCircle className="h-3.5 w-3.5 text-emerald-400" />
            <span className="font-semibold">Customer Chat</span>
          </Link>
          <span className="font-mono text-[11px] text-zinc-400">v2.4.0</span>
        </div>
      </div>
    </aside>
  );
}
