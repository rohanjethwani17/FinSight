'use client';

import { FileText } from 'lucide-react';
import { useChatStore } from '@/lib/store';
import { cn } from '@/lib/utils';

interface CitationBadgeProps {
    source: string;
    className?: string;
}

export function CitationBadge({ source, className }: CitationBadgeProps) {
    const { activeContexts, setHighlightedContextId } = useChatStore();

    // Find the context that matches this source
    const context = activeContexts.find((ctx) =>
        ctx.section_header.toLowerCase().includes(source.toLowerCase()) ||
        source.toLowerCase().includes(ctx.section_header.toLowerCase())
    );

    const handleClick = () => {
        if (context) {
            setHighlightedContextId(context.id);
        }
    };

    return (
        <button
            onClick={handleClick}
            className={cn(
                'inline-flex items-center gap-1 rounded border border-emerald-800 bg-emerald-900/30 px-1.5 py-0.5 text-[10px] font-medium text-emerald-400 transition-colors hover:bg-emerald-900/50 hover:text-emerald-300',
                className
            )}
            title={context ? 'View source context' : 'Source context not found'}
        >
            <FileText className="h-3 w-3" />
            {source}
        </button>
    );
}
