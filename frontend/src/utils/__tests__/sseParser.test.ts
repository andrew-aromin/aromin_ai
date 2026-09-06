import { describe, it, expect } from 'vitest';
import { parseSSELines } from '../sseParser';

describe('parseSSELines', () => {
  it('parses simple text data chunk', () => {
    const chunk = 'data: "Hello world"\n\n';
    const result = parseSSELines(chunk);
    expect(result.events).toEqual(['Hello world']);
    expect(result.remainingBuffer).toBe('');
  });

  it('handles multi-line chunks with multiple events', () => {
    const chunk = 'data: "Chunk 1"\n\ndata: "Chunk 2"\n\n';
    const result = parseSSELines(chunk);
    expect(result.events).toEqual(['Chunk 1', 'Chunk 2']);
    expect(result.remainingBuffer).toBe('');
  });

  it('handles partial lines across chunks using buffer', () => {
    const firstChunk = 'data: "Par';
    const firstResult = parseSSELines(firstChunk, '');
    expect(firstResult.events).toEqual([]);
    expect(firstResult.remainingBuffer).toBe('data: "Par');

    const secondChunk = 'tial line"\n\n';
    const secondResult = parseSSELines(secondChunk, firstResult.remainingBuffer);
    expect(secondResult.events).toEqual(['Partial line']);
    expect(secondResult.remainingBuffer).toBe('');
  });

  it('ignores SSE comment ping lines', () => {
    const chunk = ': ping\n\ndata: "After ping"\n\n';
    const result = parseSSELines(chunk);
    expect(result.events).toEqual(['After ping']);
  });

  it('parses JSON error objects correctly', () => {
    const chunk = 'data: {"error": "Connection timeout"}\n\n';
    const result = parseSSELines(chunk);
    expect(result.events).toEqual([{ error: 'Connection timeout' }]);
  });

  it('handles unquoted non-JSON string payloads as raw string', () => {
    const chunk = 'data: raw plain text\n\n';
    const result = parseSSELines(chunk);
    expect(result.events).toEqual(['raw plain text']);
  });

  it('ignores empty data lines', () => {
    const chunk = 'data:\n\ndata:   \n\n';
    const result = parseSSELines(chunk);
    expect(result.events).toEqual([]);
  });
});
