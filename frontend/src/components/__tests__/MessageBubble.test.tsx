import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithMantine } from '../../test/test-utils';
import MessageBubble from '../MessageBubble';
import type { Message } from '../../types/chat';

describe('MessageBubble', () => {
  const userMessage: Message = {
    role: 'user',
    content: 'What is your background?',
  };

  const assistantMessage: Message = {
    role: 'assistant',
    content: '11 years in software engineering. [LinkedIn](https://linkedin.com)',
  };

  it('renders user message with user icon and content', () => {
    renderWithMantine(<MessageBubble msg={userMessage} />);

    expect(screen.getByTestId('user-icon')).toBeInTheDocument();
    expect(screen.getByText('What is your background?')).toBeInTheDocument();
    expect(screen.getByTestId('message-bubble')).toHaveAttribute('data-role', 'user');
  });

  it('renders assistant message with cpu icon, markdown text, and link with target _blank', () => {
    renderWithMantine(<MessageBubble msg={assistantMessage} />);

    expect(screen.getByTestId('cpu-icon')).toBeInTheDocument();
    expect(screen.getByText(/11 years in software engineering\./i)).toBeInTheDocument();

    const link = screen.getByRole('link', { name: 'LinkedIn' });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://linkedin.com');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    expect(screen.getByTestId('message-bubble')).toHaveAttribute('data-role', 'assistant');
  });
});
