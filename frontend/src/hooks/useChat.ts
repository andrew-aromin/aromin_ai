import { useState } from 'react';
import type { Message } from '../types/chat';
import { sanitizeFrontendInput } from '../utils/sanitize';

/**
 * Custom hook to manage chat state and communication with the backend API.
 * Handles sending messages, receiving streaming responses, and managing loading states.
 */
export const useChat = () => {
  // State to store the history of messages in the conversation
  const [messages, setMessages] = useState<Message[]>([]);
  // State to track if a message is currently being processed
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Sends a user message to the backend and handles the streaming response.
   * @param prompt The message text entered by the user.
   */
  const sendMessage = async (prompt: string) => {
    // 1. Sanitize the user input
    const sanitizedPrompt = sanitizeFrontendInput(prompt);
    if (!sanitizedPrompt) return;

    // 2. Create and add the user's message to the local state
    const userMsg: Message = { role: 'user', content: sanitizedPrompt };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // 3. Send the message to the backend API
      // Use nullish coalescing to allow empty string (relative path)
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: sanitizedPrompt }),
      });

      if (response.status === 429) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'You are submitting too many requests. Please wait a moment and try again.',
          },
        ]);
        return;
      }

      if (!response.body) throw new Error('No response body');

      // 4. Initialize the stream reader to handle the chunked response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let botContent = '';
      let isFirstChunk = true;
      let partialLine = '';

      // 5. Continuously read chunks from the stream until completion
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        // Decode the binary chunk into text and split by newlines
        const chunk = decoder.decode(value, { stream: true });
        const lines = (partialLine + chunk).split('\n');

        // The last element might be a partial line, save it for the next iteration
        partialLine = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          // SSE lines start with "data: "
          if (trimmedLine.startsWith('data:')) {
            // Extract the data content (strip "data:" prefix)
            const rawData = trimmedLine.slice(5).trim();
            if (!rawData) continue;

            try {
              // Parse the JSON-encoded data chunk
              const data = JSON.parse(rawData);

              // Handle error objects from the backend
              if (data && typeof data === 'object' && data.error) {
                botContent += `\nError: ${data.error}`;
              } else {
                botContent += data;
              }

              if (isFirstChunk) {
                // On the first valid data chunk, append a new assistant message to the list
                setMessages((prev) => [...prev, { role: 'assistant', content: botContent }]);
                isFirstChunk = false;
              } else {
                // For subsequent chunks, update the content of the last assistant message
                setMessages((prev) => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1].content = botContent;
                  return newMessages;
                });
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, rawData);
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat Error:', error);
    } finally {
      // Ensure loading state is reset regardless of success or failure
      setIsLoading(false);
    }
  };

  return { messages, sendMessage, isLoading };
};
