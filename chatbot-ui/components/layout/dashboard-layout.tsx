'use client';

import { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './sidebar';
import { Header } from './header';
import { IsometricLoader } from '@/components/ui/isometric-loader';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Lock, ShieldAlert, Sparkles } from 'lucide-react';
import { checkAdminAuth, adminLogin, adminLogout } from '@/lib/api-client';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [adminUsername, setAdminUsername] = useState('admin');
  const [passwordInput, setPasswordInput] = useState('');
  const [loginError, setLoginError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const verifyAdmin = useCallback(async () => {
    const authData = await checkAdminAuth();
    if (authData) {
      setIsAdminAuthenticated(true);
      setAdminUsername(authData.username || 'admin');
    } else {
      setIsAdminAuthenticated(false);
    }
    setIsPageLoading(false);
  }, []);

  useEffect(() => {
    verifyAdmin();
  }, [verifyAdmin]);

  const handleAdminLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setIsSubmitting(true);
    try {
      const data = await adminLogin(adminUsername, passwordInput);
      setIsAdminAuthenticated(true);
      setAdminUsername(data.username || adminUsername);
      setPasswordInput('');
    } catch (err: any) {
      setLoginError(err.message || 'Invalid admin credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAdminLogout = async () => {
    await adminLogout();
    setIsAdminAuthenticated(false);
  };

  const handleManualReload = () => {
    setIsPageLoading(true);
    verifyAdmin();
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans flex relative">
      {/* 3D Isometric Loading Overlay */}
      {isPageLoading && <IsometricLoader text="Verifying Admin Access..." />}

      {/* Admin Login Modal Overlay when Unauthenticated */}
      {!isPageLoading && !isAdminAuthenticated && (
        <div className="fixed inset-0 z-50 bg-[#09090b]/95 backdrop-blur-md flex items-center justify-center p-4 select-none">
          <Card className="w-full max-w-md p-6 bg-[#111113] border border-zinc-800 shadow-2xl rounded-xl space-y-5">
            <div className="flex flex-col items-center text-center space-y-2">
              <div className="h-12 w-12 rounded-xl bg-emerald-950/80 border border-emerald-700/60 flex items-center justify-center text-emerald-400 shadow-[0_0_15px_rgba(52,211,153,0.2)]">
                <Lock className="h-6 w-6" />
              </div>
              <h2 className="text-xl font-bold text-zinc-50 tracking-tight flex items-center gap-2">
                <span>SupportFlow Admin Login</span>
              </h2>
              <p className="text-xs text-zinc-400 font-medium">
                Enter your administrative credentials to access operational telemetry & tools.
              </p>
            </div>

            {loginError && (
              <div className="p-3 text-xs bg-rose-950/80 border border-rose-700/60 text-rose-300 rounded-lg flex items-center gap-2 font-medium">
                <ShieldAlert className="h-4 w-4 text-rose-400 flex-shrink-0" />
                <span>{loginError}</span>
              </div>
            )}

            <form onSubmit={handleAdminLoginSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-zinc-300 uppercase tracking-wider block mb-1.5">
                  Admin Username / Identifier
                </label>
                <Input
                  type="text"
                  required
                  placeholder="admin"
                  value={adminUsername}
                  onChange={(e) => setAdminUsername(e.target.value)}
                  className="bg-[#09090b] border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-zinc-300 uppercase tracking-wider block mb-1.5">
                  Secret Access Key / Password
                </label>
                <Input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  className="bg-[#09090b] border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus:border-emerald-500"
                />
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-emerald-500 hover:bg-emerald-600 text-zinc-950 font-bold transition-all shadow-[0_0_12px_rgba(52,211,153,0.3)]"
              >
                {isSubmitting ? 'Authenticating...' : 'Authenticate Admin Session'}
              </Button>
            </form>
          </Card>
        </div>
      )}

      {/* Left Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 pl-60 flex flex-col min-w-0 min-h-screen">
        <Header onTriggerReload={handleManualReload} onAdminLogout={handleAdminLogout} adminUsername={adminUsername} />
        <main className="flex-1 p-6 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
