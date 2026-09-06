/**
 * Utility for parsing Server-Sent Events (SSE) data streams.
 */

export interface ParsedSSE {
  events: Array<string | { error: string }>;
  remainingBuffer: string;
}

/**
 * Parses raw SSE chunk data together with any pending buffer.
 *
 * @param chunk New text chunk from ReadableStream.
 * @param buffer Incomplete line buffer from preceding iteration.
 * @returns Parsed events and unresolved buffer remainder.
 */
export function parseSSELines(chunk: string, buffer: string = ''): ParsedSSE {
  const combined = buffer + chunk;
  const lines = combined.split('\n');
  // The last entry after split may be incomplete
  const remainingBuffer = lines.pop() ?? '';
  const events: Array<string | { error: string }> = [];

  for (const rawLine of lines) {
    const trimmed = rawLine.trim();
    if (!trimmed || trimmed.startsWith(':')) {
      // Ignore empty lines and SSE comments (e.g. ": ping")
      continue;
    }

    if (trimmed.startsWith('data:')) {
      const dataString = trimmed.slice(5).trim();
      if (!dataString) continue;

      try {
        const parsed = JSON.parse(dataString);
        events.push(parsed);
      } catch {
        // If not valid JSON, treat as raw text
        events.push(dataString);
      }
    }
  }

  return { events, remainingBuffer };
}
