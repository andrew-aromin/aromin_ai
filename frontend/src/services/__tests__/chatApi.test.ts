import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { sendChatMessageRequest, fetchQuickQuestions } from '../chatApi';

describe('chatApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe('sendChatMessageRequest', () => {
    it('sends POST request to /api/chat with json payload', async () => {
      const mockFetch = vi.fn().mockResolvedValue(new Response('ok'));
      vi.stubGlobal('fetch', mockFetch);

      const controller = new AbortController();
      await sendChatMessageRequest('Tell me about your career', controller.signal);

      expect(mockFetch).toHaveBeenCalledWith('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'Tell me about your career' }),
        signal: controller.signal,
      });
    });
  });

  describe('fetchQuickQuestions', () => {
    it('returns questions array when API responds with 200', async () => {
      const questions = ['Q1', 'Q2'];
      const mockFetch = vi.fn().mockResolvedValue(
        new Response(JSON.stringify(questions), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        })
      );
      vi.stubGlobal('fetch', mockFetch);

      const result = await fetchQuickQuestions();
      expect(result).toEqual(questions);
      expect(mockFetch).toHaveBeenCalledWith('/api/questions');
    });

    it('returns empty array when API responds with error status', async () => {
      const mockFetch = vi.fn().mockResolvedValue(new Response('Error', { status: 500 }));
      vi.stubGlobal('fetch', mockFetch);

      const result = await fetchQuickQuestions();
      expect(result).toEqual([]);
    });

    it('returns empty array when network error occurs', async () => {
      const mockFetch = vi.fn().mockRejectedValue(new Error('Network offline'));
      vi.stubGlobal('fetch', mockFetch);

      const result = await fetchQuickQuestions();
      expect(result).toEqual([]);
    });
  });
});
