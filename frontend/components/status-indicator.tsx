'use client';

import { useEffect, useState } from 'react';
import { Activity, Wifi, WifiOff } from 'lucide-react';
import { healthCheck } from '@/lib/api';
import { cn } from '@/lib/utils';

export function StatusIndicator() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await healthCheck();
      setIsConnected(healthy);
      setLastCheck(new Date());
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2">
      <div
        className={cn(
          'flex items-center gap-1.5 rounded-full px-2 py-1 text-xs',
          isConnected === null && 'bg-zinc-800 text-zinc-400',
          isConnected === true && 'bg-emerald-900/50 text-emerald-400',
          isConnected === false && 'bg-red-900/50 text-red-400'
        )}
      >
        {isConnected === null ? (
          <Activity className="h-3 w-3 animate-pulse" />
        ) : isConnected ? (
          <Wifi className="h-3 w-3" />
        ) : (
          <WifiOff className="h-3 w-3" />
        )}
        <span>
          {isConnected === null
            ? 'Connecting...'
            : isConnected
            ? 'Connected'
            : 'Disconnected'}
        </span>
      </div>
    </div>
  );
}
