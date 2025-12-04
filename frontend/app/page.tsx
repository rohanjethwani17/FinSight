'use client';

import { TrendingUp, BarChart3, Shield, Clock } from 'lucide-react';
import { ChatInterface } from '@/components/chat-interface';
import { ReferencePanel } from '@/components/reference-panel';
import { TickerSelector } from '@/components/ticker-selector';
import { StatusIndicator } from '@/components/status-indicator';

export default function Dashboard() {
  return (
    <div className="flex h-screen flex-col bg-zinc-950">
      {/* Top Navigation */}
      <header className="flex items-center justify-between border-b border-zinc-800 px-6 py-3">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-blue-500">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-zinc-100">
              FinSight
            </span>
          </div>
          <div className="h-6 w-px bg-zinc-800" />
          <TickerSelector />
        </div>

        <div className="flex items-center gap-4">
          <StatusIndicator />
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <Clock className="h-3.5 w-3.5" />
            <span>Real-time Analysis</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Reference/Context (60%) */}
        <div className="w-[60%] border-r border-zinc-800">
          <ReferencePanel />
        </div>

        {/* Right Panel - Chat Interface (40%) */}
        <div className="w-[40%]">
          <ChatInterface />
        </div>
      </div>

      {/* Footer */}
      <footer className="flex items-center justify-between border-t border-zinc-800 px-6 py-2">
        <div className="flex items-center gap-4 text-xs text-zinc-600">
          <div className="flex items-center gap-1">
            <BarChart3 className="h-3.5 w-3.5" />
            <span>SEC 10-K Data</span>
          </div>
          <div className="flex items-center gap-1">
            <Shield className="h-3.5 w-3.5" />
            <span>Enterprise Grade</span>
          </div>
        </div>
        <div className="text-xs text-zinc-600">
          Powered by GPT-4o-mini &middot; Pinecone Vector DB
        </div>
      </footer>
    </div>
  );
}
