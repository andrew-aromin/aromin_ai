/**
 * API service for interacting with Aromin AI backend endpoints.
 */

const getApiBaseUrl = (): string => {
  return import.meta.env.VITE_API_BASE_URL ?? '';
};

/**
 * Sends a chat message to the /api/chat endpoint and returns the Response object.
 *
 * @param message The user's prompt text.
 * @param signal Optional AbortSignal for request cancellation.
 */
export async function sendChatMessageRequest(
  message: string,
  signal?: AbortSignal
): Promise<Response> {
  const baseUrl = getApiBaseUrl();
  return fetch(`${baseUrl}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
    signal,
  });
}

/**
 * Fetches the ordered list of quick questions from the backend.
 * Returns empty array if request fails, allowing fallback to local defaults.
 */
export async function fetchQuickQuestions(): Promise<string[]> {
  try {
    const baseUrl = getApiBaseUrl();
    const res = await fetch(`${baseUrl}/api/questions`);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}
