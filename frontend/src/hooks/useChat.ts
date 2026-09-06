import { useState, useRef, useEffect, useCallback } from 'react';
import type { Message } from '../types/chat';
import { sanitizeFrontendInput } from '../utils/sanitize';
import { sendChatMessageRequest } from '../services/chatApi';
import { parseSSELines } from '../utils/sseParser';

export const RATE_LIMIT_MESSAGE =
  'You are submitting too many requests. Please wait a moment and try again.';
export const GENERIC_ERROR_MESSAGE =
  'An unexpected error occurred while communicating with the server.';

/**
 * Custom hook managing chat state, SSE streaming, and user actions.
 */
export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Clean up any ongoing request on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const abortChat = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
  }, []);

  const sendMessage = useCallback(async (prompt: string) => {
    const sanitizedPrompt = sanitizeFrontendInput(prompt);
    if (!sanitizedPrompt) return;

    // Abort any existing streaming response
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    const userMsg: Message = { role: 'user', content: sanitizedPrompt };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await sendChatMessageRequest(sanitizedPrompt, controller.signal);

      if (response.status === 429) {
        setMessages((prev) => [...prev, { role: 'assistant', content: RATE_LIMIT_MESSAGE }]);
        return;
      }

      if (!response.ok) {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: `Error ${response.status}: Failed to reach AI service.` },
        ]);
        return;
      }

      if (!response.body) {
        throw new Error('No response body received from server.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let botContent = '';
      let isFirstChunk = true;
      let pendingBuffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunkText = decoder.decode(value, { stream: true });
        const { events, remainingBuffer } = parseSSELines(chunkText, pendingBuffer);
        pendingBuffer = remainingBuffer;

        for (const ev of events) {
          if (typeof ev === 'object' && ev !== null && 'error' in ev) {
            botContent += `\nError: ${ev.error}`;
          } else if (typeof ev === 'string') {
            botContent += ev;
          }

          if (isFirstChunk) {
            setMessages((prev) => [...prev, { role: 'assistant', content: botContent }]);
            isFirstChunk = false;
          } else {
            setMessages((prev) => {
              const updated = [...prev];
              if (updated.length > 0) {
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  content: botContent,
                };
              }
              return updated;
            });
          }
        }
      }
    } catch (error: unknown) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        // Request was aborted intentionally, do not add error message
        return;
      }
      console.error('Chat Error:', error);
      setMessages((prev) => [...prev, { role: 'assistant', content: GENERIC_ERROR_MESSAGE }]);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, []);

  return { messages, sendMessage, isLoading, abortChat, setMessages };
};
