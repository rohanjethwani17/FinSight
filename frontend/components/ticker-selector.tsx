'use client';

import { useState, useEffect } from 'react';
import { ChevronDown, Building2, Check } from 'lucide-react';
import { useChatStore } from '@/lib/store';
import { getFilings } from '@/lib/api';
import { cn } from '@/lib/utils';
import { FilingInfo } from '@/types';

const companyLogos: Record<string, string> = {
  AAPL: '🍎',
  MSFT: '🪟',
  GOOGL: '🔍',
  TSLA: '🚗',
  NVDA: '👁️',
  AMZN: '📦',
};

export function TickerSelector() {
  const [isOpen, setIsOpen] = useState(false);
  const { selectedTicker, setSelectedTicker, filings, setFilings } = useChatStore();

  useEffect(() => {
    const loadFilings = async () => {
      try {
        const data = await getFilings();
        setFilings(data.filings);
      } catch (err) {
        // Use default filings if API fails
        setFilings([
          { ticker: 'AAPL', company_name: 'Apple Inc.', available: true },
          { ticker: 'MSFT', company_name: 'Microsoft Corporation', available: true },
          { ticker: 'GOOGL', company_name: 'Alphabet Inc.', available: true },
          { ticker: 'TSLA', company_name: 'Tesla, Inc.', available: true },
          { ticker: 'NVDA', company_name: 'NVIDIA Corporation', available: true },
          { ticker: 'AMZN', company_name: 'Amazon.com, Inc.', available: true },
        ]);
      }
    };
    loadFilings();
  }, [setFilings]);

  const selectedFiling = filings.find((f) => f.ticker === selectedTicker) || {
    ticker: selectedTicker,
    company_name: selectedTicker,
    available: true,
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2.5 transition-colors hover:border-zinc-600 hover:bg-zinc-700"
      >
        <span className="text-xl">{companyLogos[selectedTicker] || '📊'}</span>
        <div className="text-left">
          <div className="text-sm font-medium text-zinc-100">{selectedFiling.ticker}</div>
          <div className="text-xs text-zinc-400">{selectedFiling.company_name}</div>
        </div>
        <ChevronDown
          className={cn(
            'h-4 w-4 text-zinc-400 transition-transform',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute left-0 top-full z-20 mt-2 w-64 rounded-lg border border-zinc-700 bg-zinc-800 py-2 shadow-xl">
            <div className="px-3 pb-2">
              <span className="text-xs font-medium text-zinc-500">SELECT COMPANY</span>
            </div>
            {filings.map((filing) => (
              <button
                key={filing.ticker}
                onClick={() => {
                  setSelectedTicker(filing.ticker);
                  setIsOpen(false);
                }}
                className={cn(
                  'flex w-full items-center gap-3 px-3 py-2 text-left transition-colors hover:bg-zinc-700',
                  filing.ticker === selectedTicker && 'bg-zinc-700'
                )}
              >
                <span className="text-xl">{companyLogos[filing.ticker] || '📊'}</span>
                <div className="flex-1">
                  <div className="text-sm font-medium text-zinc-100">{filing.ticker}</div>
                  <div className="text-xs text-zinc-400">{filing.company_name}</div>
                </div>
                {filing.ticker === selectedTicker && (
                  <Check className="h-4 w-4 text-emerald-400" />
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
