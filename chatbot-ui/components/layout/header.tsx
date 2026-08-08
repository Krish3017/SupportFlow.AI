'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { useTheme } from 'next-themes';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { RotateCw, Bell, Moon, Sun, User, Settings, LogOut, Sidebar as SidebarIcon, Search } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface HeaderProps {
  onTriggerReload?: () => void;
  onAdminLogout?: () => void;
  adminUsername?: string;
}

export function Header({ onTriggerReload, onAdminLogout, adminUsername = 'admin' }: HeaderProps) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();

  const getPageTitle = (path: string) => {
    if (path === '/admin') return 'Overview';
    if (path.startsWith('/admin/conversations')) return 'Conversations';
    if (path.startsWith('/admin/tickets')) return 'Tickets';
    if (path.startsWith('/admin/customers')) return 'Customers';
    if (path.startsWith('/admin/ai-observatory')) return 'AI Observatory';
    if (path.startsWith('/admin/knowledge')) return 'Knowledge Base';
    if (path.startsWith('/admin/email')) return 'Email Center';
    if (path.startsWith('/admin/analytics')) return 'Analytics';
    if (path.startsWith('/admin/activity')) return 'Activity Log';
    if (path.startsWith('/admin/settings')) return 'Settings';
    return 'Admin';
  };

  const pageTitle = getPageTitle(pathname || '');

  return (
    <header className="flex items-center justify-between px-4 py-2 border-b border-zinc-800/80 bg-[#09090b]/90 sticky top-0 z-20 backdrop-blur select-none">
      {/* Breadcrumb Path */}
      <div className="flex items-center gap-2 text-xs">
        <span className="text-zinc-500 font-medium">/</span>
        <span className="text-zinc-400 font-medium">SupportFlow</span>
        <span className="text-zinc-600">/</span>
        <span className="font-semibold text-zinc-100">{pageTitle}</span>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 text-zinc-400">
        {/* Manual 5s Isometric Loader Trigger */}
        {onTriggerReload && (
          <button
            onClick={onTriggerReload}
            title="Reload Dashboard (5s Isometric Loader)"
            className="p-1.5 rounded-lg bg-zinc-900/80 hover:bg-zinc-800 hover:text-zinc-100 transition-colors flex items-center gap-1.5 text-xs text-zinc-300 border border-zinc-800"
          >
            <RotateCw className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Reload (5s)</span>
          </button>
        )}

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-1.5 rounded-lg hover:bg-zinc-800/80 hover:text-zinc-100 transition-colors"
          title="Toggle Theme"
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </button>

        {/* Notifications Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger className="p-1.5 rounded-lg hover:bg-zinc-800/80 hover:text-zinc-100 transition-colors relative outline-none">
            <Bell className="h-4 w-4" />
            <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80 bg-[#111113] border-zinc-800 text-zinc-100">
            <DropdownMenuLabel className="text-xs text-zinc-300">System Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-zinc-800" />
            <div className="p-2 text-xs space-y-2 text-zinc-400">
              <div className="p-2 rounded bg-zinc-900/60 border border-zinc-800">
                <div className="text-zinc-200 font-medium">All AI Agents Operational</div>
                <div className="text-[10px] text-zinc-500 mt-0.5">LangGraph multi-agent loop active.</div>
              </div>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Profile Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger className="outline-none ml-1">
            <Avatar className="h-6 w-6 ring-1 ring-zinc-700">
              <AvatarFallback className="bg-emerald-950 text-emerald-300 text-[10px] font-bold">AD</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-[#111113] border-zinc-800 text-zinc-100">
            <DropdownMenuLabel className="text-xs">
              <div className="flex flex-col">
                <span className="font-semibold text-zinc-200">Admin Supervisor</span>
                <span className="text-[10px] text-zinc-400 font-normal">{adminUsername}@supportflow.ai</span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-zinc-800" />
            {onAdminLogout && (
              <DropdownMenuItem onClick={onAdminLogout} className="text-xs hover:bg-zinc-800 text-rose-400 focus:text-rose-300 cursor-pointer">
                <LogOut className="mr-2 h-3.5 w-3.5" />
                <span>Admin Logout</span>
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
