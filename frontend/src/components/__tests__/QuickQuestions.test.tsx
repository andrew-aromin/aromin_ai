import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithMantine } from '../../test/test-utils';
import QuickQuestions from '../QuickQuestions';
import { DEFAULT_QUESTIONS } from '../../constants/questions';

describe('QuickQuestions Component', () => {
  it('renders all default questions', () => {
    renderWithMantine(<QuickQuestions onQuestionClick={vi.fn()} />);

    DEFAULT_QUESTIONS.forEach((q) => {
      expect(screen.getByText(q)).toBeInTheDocument();
    });
  });

  it('renders custom questions if provided', () => {
    const custom = ['Custom Q1', 'Custom Q2'];
    renderWithMantine(<QuickQuestions onQuestionClick={vi.fn()} questions={custom} />);

    expect(screen.getByText('Custom Q1')).toBeInTheDocument();
    expect(screen.getByText('Custom Q2')).toBeInTheDocument();
  });

  it('calls onQuestionClick with correct question when clicked', () => {
    const mockOnClick = vi.fn();
    renderWithMantine(<QuickQuestions onQuestionClick={mockOnClick} />);

    const button = screen.getByText(DEFAULT_QUESTIONS[0]);
    fireEvent.click(button);

    expect(mockOnClick).toHaveBeenCalledWith(DEFAULT_QUESTIONS[0]);
  });

  it('disables buttons when disabled prop is true', () => {
    renderWithMantine(<QuickQuestions onQuestionClick={vi.fn()} disabled={true} />);

    const button = screen.getByText(DEFAULT_QUESTIONS[0]).closest('button');
    expect(button).toBeDisabled();
  });
});
