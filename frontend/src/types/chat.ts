export type MessageRole = 'user' | 'assistant';

export interface Message {
  role: MessageRole;
  content: string;
}

export interface ChatRequest {
  message: string;
}

export interface StreamErrorPayload {
  error: string;
}
