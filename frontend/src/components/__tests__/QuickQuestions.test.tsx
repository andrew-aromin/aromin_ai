import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import QuickQuestions from '../QuickQuestions';

describe('QuickQuestions Component', () => {
  const QUESTIONS = [
    "Summarize Andrew's background",
    "Building 'Balto' ($100K+ savings)",
    "Serverless & Event-Driven design",
    "AI-augmented workflows",
    "Modernizing Artiva at Credit Acceptance"
  ];

  it('renders all questions', () => {
    render(<QuickQuestions onQuestionClick={jest.fn()} />);
    
    QUESTIONS.forEach(q => {
      expect(screen.getByText(q)).toBeInTheDocument();
    });
  });

  it('calls onQuestionClick with correct question when clicked', () => {
    const mockOnClick = jest.fn();
    render(<QuickQuestions onQuestionClick={mockOnClick} />);
    
    const button = screen.getByText(QUESTIONS[0]);
    fireEvent.click(button);
    
    expect(mockOnClick).toHaveBeenCalledWith(QUESTIONS[0]);
  });

  it('disables all buttons when disabled prop is true', () => {
    render(<QuickQuestions onQuestionClick={jest.fn()} disabled={true} />);
    
    QUESTIONS.forEach(q => {
      expect(screen.getByText(q).closest('button')).toBeDisabled();
    });
  });

  it('enables all buttons when disabled prop is false', () => {
    render(<QuickQuestions onQuestionClick={jest.fn()} disabled={false} />);
    
    QUESTIONS.forEach(q => {
      expect(screen.getByText(q).closest('button')).not.toBeDisabled();
    });
  });
});
