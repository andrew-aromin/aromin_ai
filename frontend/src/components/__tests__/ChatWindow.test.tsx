// frontend/src/components/ChatWindow.test.tsx

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import ChatWindow from './ChatWindow';
import type { Message } from '../types/chat';

describe('ChatWindow', () => {
  const messages: Message[] = [
    { role: 'user', content: 'Hello' },
    { role: 'assistant', content: 'Hi there!' }
  ];

  it('renders messages correctly', () => {
    render(<ChatWindow messages={messages} scrollRef={{ current: null }} />);

    // Check if the correct number of message bubbles are rendered
    const messageBubbles = screen.getAllByRole('listitem');
    expect(messageBubbles).toHaveLength(messages.length);

    // Check if the content of each message is rendered correctly
    messages.forEach((msg, index) => {
      const messageContent = screen.getByText(msg.content);
      expect(messageContent).toBeInTheDocument();
    });
  });

  it('renders a div with scrollRef', () => {
    render(<ChatWindow messages={messages} scrollRef={{ current: null }} />);

    // Check if the scrollRef anchor is rendered
    const scrollRefDiv = screen.getByTestId('scroll-ref');
    expect(scrollRefDiv).toBeInTheDocument();
    expect(scrollRefDiv.style.height).toBe('1px');
  });
});