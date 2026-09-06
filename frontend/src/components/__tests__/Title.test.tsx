import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithMantine } from '../../test/test-utils';
import Title from '../Title';

describe('Title Component', () => {
  it('renders the title text correctly', () => {
    renderWithMantine(<Title />);
    expect(screen.getByText(/Hi, I'm Andrew\./i)).toBeInTheDocument();
  });

  it('renders the avatar image correctly', () => {
    renderWithMantine(<Title />);
    const avatar = screen.getByAltText('Andrew Aromin');
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute('src', '/avatar.png');
  });

  it('renders the description text and source code link', () => {
    renderWithMantine(<Title />);
    expect(
      screen.getByText(/Ask questions about my software engineering career and background\./i)
    ).toBeInTheDocument();
    const sourceLink = screen.getByRole('link', { name: /Aromin AI/i });
    expect(sourceLink).toBeInTheDocument();
    expect(sourceLink).toHaveAttribute('href', 'https://github.com/andrew-aromin/aromin_ai');
  });
});
