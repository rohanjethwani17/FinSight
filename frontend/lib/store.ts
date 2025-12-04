import { create } from 'zustand';
import { ChatMessage, ContextChunk, FilingInfo } from '@/types';
import { generateId } from './utils';

interface ChatState {
  // Selected ticker
  selectedTicker: string;
  setSelectedTicker: (ticker: string) => void;

  // Available filings
  filings: FilingInfo[];
  setFilings: (filings: FilingInfo[]) => void;

  // Chat messages
  messages: ChatMessage[];
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => string;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  appendToMessage: (id: string, content: string) => void;
  clearMessages: () => void;

  // Active contexts (for the reference panel)
  activeContexts: ContextChunk[];
  setActiveContexts: (contexts: ContextChunk[]) => void;

  // UI State
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Selected ticker
  selectedTicker: 'AAPL',
  setSelectedTicker: (ticker) => {
    set({ selectedTicker: ticker, messages: [], activeContexts: [] });
  },

  // Available filings
  filings: [],
  setFilings: (filings) => set({ filings }),

  // Chat messages
  messages: [],
  addMessage: (message) => {
    const id = generateId();
    const newMessage: ChatMessage = {
      ...message,
      id,
      timestamp: new Date(),
    };
    set((state) => ({ messages: [...state.messages, newMessage] }));
    return id;
  },
  updateMessage: (id, updates) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, ...updates } : msg
      ),
    }));
  },
  appendToMessage: (id, content) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content: msg.content + content } : msg
      ),
    }));
  },
  clearMessages: () => set({ messages: [], activeContexts: [] }),

  // Active contexts
  activeContexts: [],
  setActiveContexts: (contexts) => set({ activeContexts: contexts }),

  // UI State
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),
  error: null,
  setError: (error) => set({ error }),
}));
