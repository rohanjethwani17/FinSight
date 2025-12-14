'use client';

import { FileText, ExternalLink, ChevronDown, ChevronUp, TrendingUp } from 'lucide-react';
import { useChatStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';

export function ReferencePanel() {
  const { activeContexts, selectedTicker, highlightedContextId, setHighlightedContextId } = useChatStore();
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  // Scroll to highlighted context
  useEffect(() => {
    if (highlightedContextId) {
      const element = document.getElementById(`context-${highlightedContextId}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Auto-expand the highlighted context
        const index = activeContexts.findIndex(c => c.id === highlightedContextId);
        if (index !== -1) {
          setExpandedIndex(index);
        }
        // Clear highlight after animation
        setTimeout(() => setHighlightedContextId(null), 2000);
      }
    }
  }, [highlightedContextId, activeContexts, setHighlightedContextId]);

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-emerald-400 bg-emerald-900/30';
    if (score >= 0.8) return 'text-blue-400 bg-blue-900/30';
    if (score >= 0.7) return 'text-yellow-400 bg-yellow-900/30';
    return 'text-zinc-400 bg-zinc-800';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.9) return 'High';
    if (score >= 0.8) return 'Good';
    if (score >= 0.7) return 'Fair';
    return 'Low';
  };

  return (
    <div className="flex h-full flex-col bg-zinc-900">
      {/* Header */}
      <div className="border-b border-zinc-800 px-3 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-500" />
            <span className="font-semibold text-zinc-100">Document Context</span>
          </div>
          {activeContexts.length > 0 && (
            <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">
              {activeContexts.length} sources
            </span>
          )}
        </div>
        <p className="mt-1 text-xs text-zinc-500">
          SEC 10-K filing excerpts used to answer your query
        </p>
      </div>

      {/* Context List */}
      <div className="flex-1 overflow-y-auto">
        {activeContexts.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center p-6 text-center">
            <div className="rounded-full bg-zinc-800 p-4">
              <TrendingUp className="h-8 w-8 text-zinc-600" />
            </div>
            <h3 className="mt-4 text-sm font-medium text-zinc-400">
              No active references
            </h3>
            <p className="mt-2 max-w-xs text-xs text-zinc-600">
              When you ask a question, relevant excerpts from {selectedTicker}&apos;s SEC 10-K
              filings will appear here with relevance scores.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-zinc-800">
            {activeContexts.map((context, index) => (
              <div
                key={context.id}
                id={`context-${context.id}`}
                className={cn(
                  "group transition-colors duration-500",
                  highlightedContextId === context.id && "bg-yellow-900/20 ring-1 ring-yellow-500/50"
                )}
              >
                <button
                  onClick={() => toggleExpand(index)}
                  className="flex w-full items-start gap-3 px-3 py-2 text-left transition-colors hover:bg-zinc-800/50"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-zinc-200 text-sm">
                        {context.section_header}
                      </span>
                      <span className="text-xs text-zinc-500">{context.year}</span>
                    </div>
                    <div className="mt-1 flex items-center gap-2">
                      <span
                        className={cn(
                          'rounded px-1.5 py-0.5 text-xs font-mono',
                          getScoreColor(context.score)
                        )}
                      >
                        {(context.score * 100).toFixed(1)}% {getScoreLabel(context.score)}
                      </span>
                    </div>
                  </div>
                  <div className="shrink-0 pt-0.5">
                    {expandedIndex === index ? (
                      <ChevronUp className="h-4 w-4 text-zinc-500" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-zinc-500" />
                    )}
                  </div>
                </button>

                {/* Expanded content */}
                {expandedIndex === index && (
                  <div className="bg-zinc-800/30 px-4 pb-4">
                    <div className="rounded-lg border border-zinc-700 bg-zinc-900 p-3">
                      <p className="font-mono text-xs leading-relaxed text-zinc-300">
                        {context.text_content}
                      </p>
                    </div>
                    {context.source_url && (
                      <a
                        href={context.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-2 inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                      >
                        <ExternalLink className="h-3 w-3" />
                        View SEC Filing
                      </a>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer info */}
      {activeContexts.length > 0 && (
        <div className="border-t border-zinc-800 px-4 py-2">
          <p className="text-xs text-zinc-600">
            Relevance scores indicate semantic similarity to your query
          </p>
        </div>
      )}
    </div>
  );
}
