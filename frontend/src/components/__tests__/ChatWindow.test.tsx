import React from 'react';
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithMantine } from '../../test/test-utils';
import ChatWindow from '../ChatWindow';
import type { Message } from '../../types/chat';

describe('ChatWindow Component', () => {
  const messages: Message[] = [
    { role: 'user', content: 'What is your background?' },
    { role: 'assistant', content: 'I have 11 years of engineering experience.' },
  ];

  it('renders all messages and scroll anchor', () => {
    const scrollRef = React.createRef<HTMLDivElement>();
    renderWithMantine(<ChatWindow messages={messages} showTyping={false} scrollRef={scrollRef} />);

    expect(screen.getByText('What is your background?')).toBeInTheDocument();
    expect(screen.getByText('I have 11 years of engineering experience.')).toBeInTheDocument();
    expect(screen.getByTestId('scroll-anchor')).toBeInTheDocument();
    expect(screen.queryByTestId('typing-indicator')).not.toBeInTheDocument();
  });

  it('renders TypingIndicator when showTyping is true', () => {
    const scrollRef = React.createRef<HTMLDivElement>();
    renderWithMantine(<ChatWindow messages={messages} showTyping={true} scrollRef={scrollRef} />);

    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
  });
});
