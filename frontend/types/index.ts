// Type definitions for FinSight

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  contexts?: ContextChunk[];
  timestamp: Date;
}

export interface ContextChunk {
  id: string;
  score: number;
  text_content: string;
  section_header: string;
  source_url: string;
  year: string;
}

export interface FilingInfo {
  ticker: string;
  company_name: string;
  available: boolean;
}

export interface ChatRequest {
  message: string;
  ticker: string;
  history: { role: string; content: string }[];
}

export interface StreamEvent {
  type: 'contexts' | 'token' | 'done';
  data?: ContextChunk[] | string;
}
