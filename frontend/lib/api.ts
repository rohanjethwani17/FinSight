const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api';

export interface ChatHistoryItem {
  role: string;
  content: string;
}

export interface ContextChunk {
  id: string;
  score: number;
  text_content: string;
  section_header: string;
  source_url: string;
  year: string;
}

export interface StreamEvent {
  type: 'contexts' | 'token' | 'done';
  data?: ContextChunk[] | string;
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export async function getFilings() {
  const response = await fetch(`${API_URL}/filings`);
  if (!response.ok) {
    throw new Error('Failed to fetch filings');
  }
  return response.json();
}

export async function* streamChat(
  message: string,
  ticker: string,
  history: ChatHistoryItem[]
): AsyncGenerator<StreamEvent, void, unknown> {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      ticker,
      history,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to send message');
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.trim()) {
        try {
          const event: StreamEvent = JSON.parse(line);
          yield event;
        } catch {
          // Skip invalid JSON lines
        }
      }
    }
  }

  // Process any remaining buffer
  if (buffer.trim()) {
    try {
      const event: StreamEvent = JSON.parse(buffer);
      yield event;
    } catch {
      // Skip invalid JSON
    }
  }
}
