import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithMantine } from '../test/test-utils';
import App from '../App';
import * as chatApi from '../services/chatApi';

describe('App Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(chatApi, 'fetchQuickQuestions').mockResolvedValue([
      'Custom Question 1',
      'Custom Question 2',
    ]);
  });

  it('renders initial view with Header, Title, and fetched QuickQuestions', async () => {
    renderWithMantine(<App />);

    expect(screen.getByText(/Hi, I'm Andrew\./i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ask about my career\.\.\./i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Custom Question 1')).toBeInTheDocument();
    });
  });

  it('submits message and renders ChatWindow upon sending', async () => {
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('data: "AI response chunk"\n\n'));
        controller.close();
      },
    });

    vi.spyOn(chatApi, 'sendChatMessageRequest').mockResolvedValue(
      new Response(stream, { status: 200 })
    );

    renderWithMantine(<App />);

    const textarea = screen.getByPlaceholderText(/Ask about my career\.\.\./i);
    fireEvent.change(textarea, { target: { value: 'Summarize career' } });

    const sendBtn = screen.getByRole('button', { name: /Send message/i });
    fireEvent.click(sendBtn);

    // Initial title should disappear
    await waitFor(() => {
      expect(screen.queryByText(/Hi, I'm Andrew\./i)).not.toBeInTheDocument();
      expect(screen.getByText('Summarize career')).toBeInTheDocument();
      expect(screen.getByText('AI response chunk')).toBeInTheDocument();
    });
  });

  it('sends message when clicking a quick question bubble', async () => {
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('data: "Answer to question 1"\n\n'));
        controller.close();
      },
    });

    vi.spyOn(chatApi, 'sendChatMessageRequest').mockResolvedValue(
      new Response(stream, { status: 200 })
    );

    renderWithMantine(<App />);

    await waitFor(() => {
      expect(screen.getByText('Custom Question 1')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Custom Question 1'));

    await waitFor(() => {
      expect(screen.getByText('Custom Question 1')).toBeInTheDocument();
      expect(screen.getByText('Answer to question 1')).toBeInTheDocument();
    });
  });
});
