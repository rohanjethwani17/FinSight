'use client';

import { useState, useRef, useEffect, FormEvent, KeyboardEvent } from 'react';
import { Send, Loader2, Bot, User, AlertCircle, Trash2 } from 'lucide-react';
import { useChatStore } from '@/lib/store';
import { streamChat, ContextChunk } from '@/lib/api';
import { cn, formatTimestamp } from '@/lib/utils';

export function ChatInterface() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const {
    selectedTicker,
    messages,
    addMessage,
    appendToMessage,
    updateMessage,
    clearMessages,
    setActiveContexts,
    isLoading,
    setIsLoading,
    error,
    setError,
  } = useChatStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e?: FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);

    // Add user message
    addMessage({ role: 'user', content: userMessage });

    // Add placeholder for assistant message
    const assistantId = addMessage({ role: 'assistant', content: '' });

    setIsLoading(true);

    try {
      // Build chat history (exclude the current messages we just added)
      const history = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Stream the response
      let receivedContexts = false;
      for await (const event of streamChat(userMessage, selectedTicker, history)) {
        if (event.type === 'contexts') {
          const contexts = event.data as ContextChunk[];
          setActiveContexts(contexts);
          updateMessage(assistantId, { contexts });
          receivedContexts = true;
        } else if (event.type === 'token') {
          appendToMessage(assistantId, event.data as string);
        } else if (event.type === 'done') {
          // Streaming complete
        }
      }

      if (!receivedContexts) {
        setActiveContexts([]);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      updateMessage(assistantId, {
        content: `Error: ${errorMessage}`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  return (
    <div className="flex h-full flex-col bg-zinc-950">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-emerald-500" />
          <span className="font-semibold text-zinc-100">FinSight AI</span>
          <span className="rounded bg-emerald-900/50 px-2 py-0.5 text-xs text-emerald-400">
            {selectedTicker}
          </span>
        </div>
        <button
          onClick={clearMessages}
          className="rounded p-1.5 text-zinc-500 transition-colors hover:bg-zinc-800 hover:text-zinc-300"
          title="Clear chat"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <Bot className="h-12 w-12 text-zinc-700" />
            <h3 className="mt-4 text-lg font-medium text-zinc-300">
              Start analyzing {selectedTicker}
            </h3>
            <p className="mt-2 max-w-sm text-sm text-zinc-500">
              Ask questions about SEC 10-K filings. I&apos;ll retrieve relevant sections and provide
              cited analysis.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {[
                'What are the main risk factors?',
                'Summarize the business overview',
                'What are the key financial metrics?',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="rounded-full border border-zinc-700 px-3 py-1.5 text-xs text-zinc-400 transition-colors hover:border-zinc-600 hover:bg-zinc-800 hover:text-zinc-300"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.role === 'assistant' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-900/50">
                    <Bot className="h-4 w-4 text-emerald-400" />
                  </div>
                )}
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg px-4 py-2.5',
                    message.role === 'user'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-zinc-800 text-zinc-100'
                  )}
                >
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {message.content || (
                      <span className="flex items-center gap-2 text-zinc-400">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Analyzing...
                      </span>
                    )}
                  </div>
                  <div
                    className={cn(
                      'mt-1 text-xs',
                      message.role === 'user' ? 'text-emerald-200' : 'text-zinc-500'
                    )}
                  >
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
                {message.role === 'user' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-700">
                    <User className="h-4 w-4 text-zinc-300" />
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="mx-4 mb-2 flex items-center gap-2 rounded-lg bg-red-900/30 px-3 py-2 text-sm text-red-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Input */}
      <div className="border-t border-zinc-800 p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask about ${selectedTicker} 10-K filings...`}
              disabled={isLoading}
              rows={1}
              className="w-full resize-none rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2.5 pr-12 text-sm text-zinc-100 placeholder-zinc-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:opacity-50"
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-600 text-white transition-colors hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </form>
        <p className="mt-2 text-center text-xs text-zinc-600">
          Responses are based on SEC 10-K filings. Always verify important information.
        </p>
      </div>
    </div>
  );
}
