'use client';

import { useState, useEffect } from 'react';
import { Sidebar } from './sidebar';
import { Header } from './header';
import { IsometricLoader } from '@/components/ui/isometric-loader';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [isPageLoading, setIsPageLoading] = useState(true);

  // Initial loading spinner simulation on route mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsPageLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  const handleManualReload = () => {
    setIsPageLoading(true);
    setTimeout(() => {
      setIsPageLoading(false);
    }, 5000);
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-50 font-sans flex">
      {/* 3D Isometric Loading Overlay */}
      {isPageLoading && <IsometricLoader text="Loading SupportFlow System..." />}

      {/* Left Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 pl-56 flex flex-col min-w-0 min-h-screen">
        <Header onTriggerReload={handleManualReload} />
        <main className="flex-1 p-5 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
