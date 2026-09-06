import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithMantine } from '../../test/test-utils';
import UserInput from '../UserInput';

describe('UserInput Component', () => {
  it('renders Title and QuickQuestions when isInitial is true', () => {
    renderWithMantine(
      <UserInput
        input=""
        setInput={vi.fn()}
        onSend={vi.fn()}
        isLoading={false}
        isInitial={true}
        onQuickQuestion={vi.fn()}
      />
    );

    expect(screen.getByText(/Hi, I'm Andrew\./i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ask about my career\.\.\./i)).toBeInTheDocument();
  });

  it('hides Title when isInitial is false', () => {
    renderWithMantine(
      <UserInput
        input=""
        setInput={vi.fn()}
        onSend={vi.fn()}
        isLoading={false}
        isInitial={false}
        onQuickQuestion={vi.fn()}
      />
    );

    expect(screen.queryByText(/Hi, I'm Andrew\./i)).not.toBeInTheDocument();
  });

  it('calls setInput when typing in the textarea', () => {
    const mockSetInput = vi.fn();
    renderWithMantine(
      <UserInput
        input=""
        setInput={mockSetInput}
        onSend={vi.fn()}
        isLoading={false}
        isInitial={false}
        onQuickQuestion={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ask about my career\.\.\./i);
    fireEvent.change(textarea, { target: { value: 'Tell me about Balto' } });

    expect(mockSetInput).toHaveBeenCalledWith('Tell me about Balto');
  });

  it('calls onSend when Enter is pressed without Shift', () => {
    const mockOnSend = vi.fn();
    renderWithMantine(
      <UserInput
        input="Hello"
        setInput={vi.fn()}
        onSend={mockOnSend}
        isLoading={false}
        isInitial={false}
        onQuickQuestion={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ask about my career\.\.\./i);
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });

    expect(mockOnSend).toHaveBeenCalledOnce();
  });

  it('does not call onSend when Shift+Enter is pressed', () => {
    const mockOnSend = vi.fn();
    renderWithMantine(
      <UserInput
        input="Hello"
        setInput={vi.fn()}
        onSend={mockOnSend}
        isLoading={false}
        isInitial={false}
        onQuickQuestion={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ask about my career\.\.\./i);
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });

    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it('calls onSend when clicking the send action icon', () => {
    const mockOnSend = vi.fn();
    renderWithMantine(
      <UserInput
        input="Hello"
        setInput={vi.fn()}
        onSend={mockOnSend}
        isLoading={false}
        isInitial={false}
        onQuickQuestion={vi.fn()}
      />
    );

    const button = screen.getByRole('button', { name: /Send message/i });
    expect(button).not.toBeDisabled();
    fireEvent.click(button);

    expect(mockOnSend).toHaveBeenCalledOnce();
  });

  it('disables send button when input is empty', () => {
    renderWithMantine(
      <UserInput
        input="   "
        setInput={vi.fn()}
        onSend={vi.fn()}
        isLoading={false}
        isInitial={false}
        onQuickQuestion={vi.fn()}
      />
    );

    const button = screen.getByRole('button', { name: /Send message/i });
    expect(button).toBeDisabled();
  });

  it('shows Loader and disables button when isLoading is true', () => {
    renderWithMantine(
      <UserInput
        input="Hello"
        setInput={vi.fn()}
        onSend={vi.fn()}
        isLoading={true}
        isInitial={false}
        onQuickQuestion={vi.fn()}
      />
    );

    const button = screen.getByRole('button', { name: /Send message/i });
    expect(button).toBeDisabled();
    expect(screen.getByTestId('send-loader')).toBeInTheDocument();
  });
});
