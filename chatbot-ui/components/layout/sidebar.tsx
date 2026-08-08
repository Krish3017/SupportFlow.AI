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
  FileText,
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
      { name: 'AI Observatory', href: '/admin/ai-observatory', icon: Microscope, badge: '6 Agents', badgeColor: 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60' },
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
    <aside className="w-56 bg-[#09090b] border-r border-zinc-800/80 p-3 flex flex-col justify-between flex-shrink-0 h-screen fixed left-0 top-0 z-30 select-none">
      <div>
        {/* Brand Logo Header */}
        <div className="flex items-center gap-2.5 px-2 py-2 mb-4 border-b border-zinc-800/60">
          <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-zinc-950 font-bold text-xs shadow-[0_0_12px_rgba(52,211,153,0.3)]">
            <Sparkles className="h-4 w-4 fill-zinc-950" />
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-bold text-zinc-50 tracking-tight">SupportFlow AI</span>
            <span className="text-[9px] text-zinc-500 font-medium">Multi-Agent System</span>
          </div>
        </div>

        {/* Grouped Navigation */}
        <nav className="space-y-4">
          {navGroups.map((group) => (
            <div key={group.groupName}>
              <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-wider mb-1.5 px-2">
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
                          'w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all group',
                          isActive
                            ? 'bg-zinc-800/90 text-zinc-50 font-semibold border border-zinc-700/50 shadow-sm'
                            : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/40'
                        )}
                      >
                        <div className="flex items-center gap-2.5">
                          <Icon
                            className={cn(
                              'h-3.5 w-3.5 transition-colors',
                              isActive ? 'text-emerald-400' : 'text-zinc-400 group-hover:text-zinc-200'
                            )}
                          />
                          <span>{item.name}</span>
                        </div>

                        {item.badge !== undefined && (
                          <span
                            className={cn(
                              'text-[9px] font-medium px-1.5 py-0.2 rounded-full border',
                              item.badgeColor || 'bg-zinc-800 text-zinc-300 border-zinc-700/50'
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
      <div className="space-y-2 pt-2 border-t border-zinc-800/60">
        <div className="p-2 rounded-lg bg-zinc-900/60 border border-zinc-800/60 text-[10px]">
          <div className="text-[9px] text-emerald-400 uppercase tracking-wider font-bold">
            System Online
          </div>
          <div className="font-semibold text-zinc-200 mt-0.5">FastAPI & LangGraph</div>
          <div className="text-[9px] text-zinc-400">Groq LLM Active</div>
        </div>

        <div className="flex items-center justify-between text-[10px] text-zinc-500 px-1 pt-1">
          <Link href="/chat" className="flex items-center gap-1 hover:text-zinc-300 transition-colors">
            <HelpCircle className="h-3 w-3" />
            <span>Chatbot</span>
          </Link>
          <span>v2.4.0</span>
        </div>
      </div>
    </aside>
  );
}
