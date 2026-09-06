import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChat, RATE_LIMIT_MESSAGE, GENERIC_ERROR_MESSAGE } from '../useChat';
import * as chatApi from '../../services/chatApi';

describe('useChat hook', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('initializes with empty messages and isLoading false', () => {
    const { result } = renderHook(() => useChat());
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it('ignores empty or whitespace-only messages', async () => {
    const apiSpy = vi.spyOn(chatApi, 'sendChatMessageRequest');
    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('   ');
    });

    expect(apiSpy).not.toHaveBeenCalled();
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it('handles rate limit 429 response', async () => {
    vi.spyOn(chatApi, 'sendChatMessageRequest').mockResolvedValue(
      new Response('Rate limited', { status: 429 })
    );

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.messages).toEqual([
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: RATE_LIMIT_MESSAGE },
    ]);
  });

  it('handles server non-200 error', async () => {
    vi.spyOn(chatApi, 'sendChatMessageRequest').mockResolvedValue(
      new Response('Server Error', { status: 500 })
    );

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.messages).toEqual([
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: 'Error 500: Failed to reach AI service.' },
    ]);
  });

  it('handles successful streaming chunks', async () => {
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('data: "Hello "\n\n'));
        controller.enqueue(new TextEncoder().encode('data: "world!"\n\n'));
        controller.close();
      },
    });

    vi.spyOn(chatApi, 'sendChatMessageRequest').mockResolvedValue(
      new Response(stream, { status: 200 })
    );

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.messages).toEqual([
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: 'Hello world!' },
    ]);
  });

  it('handles error payload inside SSE stream', async () => {
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('data: "Initial text"\n\n'));
        controller.enqueue(new TextEncoder().encode('data: {"error": "LLM crashed"}\n\n'));
        controller.close();
      },
    });

    vi.spyOn(chatApi, 'sendChatMessageRequest').mockResolvedValue(
      new Response(stream, { status: 200 })
    );

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.messages[1].content).toContain('Initial text');
    expect(result.current.messages[1].content).toContain('Error: LLM crashed');
  });

  it('handles fetch network exception gracefully', async () => {
    vi.spyOn(chatApi, 'sendChatMessageRequest').mockRejectedValue(new Error('Failed to fetch'));

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.messages).toEqual([
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: GENERIC_ERROR_MESSAGE },
    ]);
  });

  it('allows aborting ongoing chat request', async () => {
    let controllerCaptured: AbortSignal | undefined;
    vi.spyOn(chatApi, 'sendChatMessageRequest').mockImplementation((_msg, signal) => {
      controllerCaptured = signal;
      return new Promise(() => {}); // Never resolves
    });

    const { result } = renderHook(() => useChat());

    act(() => {
      result.current.sendMessage('Hello');
    });

    expect(result.current.isLoading).toBe(true);

    act(() => {
      result.current.abortChat();
    });

    expect(result.current.isLoading).toBe(false);
    expect(controllerCaptured?.aborted).toBe(true);
  });
});
