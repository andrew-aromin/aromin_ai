import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import MessageBubble from './MessageBubble';
import type { Message } from '../types/chat';

describe('MessageBubble', () => {
  const userMessage: Message = {
    role: 'user',
    content: '**Hello, world!** [Link](https://example.com)',
  };

  const botMessage: Message = {
    role: 'bot',
    content: '**Hi there!** [Visit us](https://example.com)',
  };

  it('renders user message with correct styles and icons', () => {
    const { getByText, getByRole } = render(<MessageBubble msg={userMessage} />);
    
    expect(getByRole('img', { name: /user/i })).toBeInTheDocument();
    expect(getByText('Hello, world!')).toHaveStyle({ color: '#4dabf7' });
    expect(getByText('Link')).toHaveAttribute('href', 'https://example.com');
    expect(getByText('Link')).toHaveAttribute('target', '_blank');
  });

  it('renders bot message with correct styles and icons', () => {
    const { getByText, getByRole } = render(<MessageBubble msg={botMessage} />);
    
    expect(getByRole('img', { name: /cpu/i })).toBeInTheDocument();
    expect(getByText('Hi there!')).toHaveStyle({ color: '#4dabf7' });
    expect(getByText('Visit us')).toHaveAttribute('href', 'https://example.com');
    expect(getByText('Visit us')).toHaveAttribute('target', '_blank');
  });

  it('aligns user message to the right', () => {
    const { container } = render(<MessageBubble msg={userMessage} />);
    
    expect(container.firstChild).toHaveStyle({ justifyContent: 'flex-end' });
  });

  it('aligns bot message to the left', () => {
    const { container } = render(<MessageBubble msg={botMessage} />);
    
    expect(container.firstChild).toHaveStyle({ justifyContent: 'flex-start' });
  });
});