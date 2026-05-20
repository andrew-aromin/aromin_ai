import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect'; // for additional matchers like toBeInTheDocument
import Header from './Header';

describe('Header Component', () => {
  it('renders the avatar with correct src and alt text', () => {
    const { getByAltText } = render(<Header />);
    const avatar = getByAltText('Andrew Aromin');
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute('src', '/avatar.png');
  });

  it('renders LinkedIn link with correct href and label', () => {
    const { getByText, getByRole } = render(<Header />);
    const linkedinLink = getByRole('link', { name: /linkedin/i });
    expect(linkedinLink).toBeInTheDocument();
    expect(linkedinLink).toHaveAttribute('href', 'https://linkedin.com/in/andrew-aromin');
  });

  it('renders GitHub link with correct href and label', () => {
    const { getByText, getByRole } = render(<Header />);
    const githubLink = getByRole('link', { name: /github/i });
    expect(githubLink).toBeInTheDocument();
    expect(githubLink).toHaveAttribute('href', 'https://github.com/andrew-aromin');
  });

  it('renders Resume link with correct href and label', () => {
    const { getByText, getByRole } = render(<Header />);
    const resumeLink = getByRole('link', { name: /resume/i });
    expect(resumeLink).toBeInTheDocument();
    expect(resumeLink).toHaveAttribute('href', '/resume.pdf');
  });

  it('displays the correct text for LinkedIn, GitHub, and Resume links', () => {
    const { getByText } = render(<Header />);
    expect(getByText(/linkedin/i)).toBeInTheDocument();
    expect(getByText(/github/i)).toBeInTheDocument();
    expect(getByText(/resume/i)).toBeInTheDocument();
  });
});