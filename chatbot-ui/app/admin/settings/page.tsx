'use client';

import { useState } from 'react';
import { Building, Bot, Plug, Bell, Shield, Users, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('workspace');

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold tracking-tight text-zinc-50">System Settings</h1>
        <p className="text-xs text-zinc-400">Configure LLM providers, multi-agent parameters & channel webhooks</p>
      </div>

      {/* Settings Tabs */}
      <div className="flex items-center bg-[#111113] border border-zinc-800 p-1 rounded-xl gap-1 overflow-x-auto">
        {[
          { id: 'workspace', label: 'Workspace', icon: Building },
          { id: 'agents', label: 'AI Agents', icon: Bot },
          { id: 'integrations', label: 'Integrations', icon: Plug },
          { id: 'security', label: 'Security & Keys', icon: Shield },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex-shrink-0',
                isActive
                  ? 'bg-zinc-800 text-zinc-50 border border-zinc-700/60 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              )}
            >
              <Icon className={cn('h-3.5 w-3.5', isActive ? 'text-emerald-400' : 'text-zinc-400')} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-5 text-xs text-zinc-300">
        {activeTab === 'workspace' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-100">Workspace Configuration</h3>
            <div className="space-y-3 max-w-lg">
              <div>
                <label className="text-[10px] text-zinc-400 font-bold uppercase block mb-1">Company Name</label>
                <input
                  type="text"
                  defaultValue="SupportFlow AI Inc."
                  className="w-full bg-[#09090b] border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-[10px] text-zinc-400 font-bold uppercase block mb-1">Support Email Address</label>
                <input
                  type="text"
                  defaultValue="krishramanandi30@gmail.com"
                  className="w-full bg-[#09090b] border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-100">Multi-Agent Engine Settings</h3>
            <div className="space-y-3 max-w-lg">
              <div className="p-3 bg-[#09090b] border border-zinc-800 rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-semibold text-zinc-100 block">LLM Provider Model</span>
                  <span className="text-[10px] text-zinc-500">llama-3.3-70b-versatile (Groq API)</span>
                </div>
                <span className="text-[9px] text-emerald-400 font-bold bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                  Active
                </span>
              </div>
              <div className="p-3 bg-[#09090b] border border-zinc-800 rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-semibold text-zinc-100 block">Orchestrator Framework</span>
                  <span className="text-[10px] text-zinc-500">LangGraph Multi-Agent State Graph</span>
                </div>
                <span className="text-[9px] text-emerald-400 font-bold bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                  Active
                </span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'integrations' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-100">Active Channel Integrations</h3>
            <div className="space-y-2">
              <div className="p-3 bg-[#09090b] border border-zinc-800 rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-semibold text-zinc-100 block">Gmail API Polling</span>
                  <span className="text-[10px] text-zinc-500">OAuth2 Token authenticated</span>
                </div>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="p-3 bg-[#09090b] border border-zinc-800 rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-semibold text-zinc-100 block">Resend API Gateway</span>
                  <span className="text-[10px] text-zinc-500">Outbound email sending enabled</span>
                </div>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="p-3 bg-[#09090b] border border-zinc-800 rounded-lg flex items-center justify-between">
                <div>
                  <span className="font-semibold text-zinc-100 block">Telegram Bot API</span>
                  <span className="text-[10px] text-zinc-500">Long-polling bot worker active</span>
                </div>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-100">API Credentials & Environment</h3>
            <div className="p-3 bg-[#09090b] border border-zinc-800 rounded-lg text-xs space-y-1">
              <span className="text-zinc-500">Environment file:</span>
              <span className="font-mono text-zinc-300 block">backend/.env</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
