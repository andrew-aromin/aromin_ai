import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import UserInput from '../UserInput';

describe('UserInput Component', () => {
  it('renders the component correctly when isInitial is true', () => {
    render(<UserInput input="" setInput={jest.fn()} onSend={jest.fn()} isLoading={false} isInitial={true} onQuickQuestion={jest.fn()} />);
    
    expect(screen.getByText(/Ask about my career\.\.\./i)).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('renders the component correctly when isInitial is false', () => {
    render(<UserInput input="" setInput={jest.fn()} onSend={jest.fn()} isLoading={false} isInitial={false} onQuickQuestion={jest.fn()} />);
    
    expect(screen.queryByText(/Ask about my career\.\.\./i)).not.toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onSend when the send button is clicked', () => {
    const mockOnSend = jest.fn();
    render(<UserInput input="Hello" setInput={jest.fn()} onSend={mockOnSend} isLoading={false} isInitial={true} onQuickQuestion={jest.fn()} />);
    
    fireEvent.click(screen.getByRole('button'));
    
    expect(mockOnSend).toHaveBeenCalled();
  });

  it('calls onSend when Enter key is pressed', () => {
    const mockOnSend = jest.fn();
    render(<UserInput input="Hello" setInput={jest.fn()} onSend={mockOnSend} isLoading={false} isInitial={true} onQuickQuestion={jest.fn()} />);
    
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Enter' });
    
    expect(mockOnSend).toHaveBeenCalled();
  });

  it('does not call onSend when Shift + Enter is pressed', () => {
    const mockOnSend = jest.fn();
    render(<UserInput input="Hello" setInput={jest.fn()} onSend={mockOnSend} isLoading={false} isInitial={true} onQuickQuestion={jest.fn()} />);
    
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Enter', shiftKey: true });
    
    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it('disables the send button when input is empty', () => {
    render(<UserInput input="" setInput={jest.fn()} onSend={jest.fn()} isLoading={false} isInitial={true} onQuickQuestion={jest.fn()} />);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('disables the send button when isLoading is true', () => {
    render(<UserInput input="Hello" setInput={jest.fn()} onSend={jest.fn()} isLoading={true} isInitial={true} onQuickQuestion={jest.fn()} />);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('enables the send button when input is not empty and isLoading is false', () => {
    render(<UserInput input="Hello" setInput={jest.fn()} onSend={jest.fn()} isLoading={false} isInitial={true} onQuickQuestion={jest.fn()} />);
    
    const button = screen.getByRole('button');
    expect(button).not.toBeDisabled();
  });
});