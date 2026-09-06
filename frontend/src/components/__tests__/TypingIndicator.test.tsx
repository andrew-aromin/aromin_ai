import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithMantine } from '../../test/test-utils';
import TypingIndicator from '../TypingIndicator';

describe('TypingIndicator', () => {
  it('renders the Avatar with Cpu icon', () => {
    renderWithMantine(<TypingIndicator />);
    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
    expect(screen.getByTestId('cpu-icon')).toBeInTheDocument();
  });

  it('renders three typing dots', () => {
    renderWithMantine(<TypingIndicator />);
    const dots = screen.getAllByTestId('typing-dot');
    expect(dots).toHaveLength(3);
  });
});
