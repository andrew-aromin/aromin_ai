import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { AppShell } from '@mantine/core';
import { renderWithMantine } from '../../../test/test-utils';
import Header from '../Header';

describe('Header Component', () => {
  const renderHeader = () =>
    renderWithMantine(
      <AppShell header={{ height: 60 }}>
        <Header />
      </AppShell>
    );

  it('renders the avatar with correct src and alt text', () => {
    renderHeader();
    const avatar = screen.getByAltText('Andrew Aromin');
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute('src', '/avatar.png');
  });

  it('renders LinkedIn link with correct href and label', () => {
    renderHeader();
    const linkedinLink = screen.getByRole('link', { name: /linkedin/i });
    expect(linkedinLink).toBeInTheDocument();
    expect(linkedinLink).toHaveAttribute('href', 'https://linkedin.com/in/andrew-aromin');
  });

  it('renders GitHub link with correct href and label', () => {
    renderHeader();
    const githubLink = screen.getByRole('link', { name: /github/i });
    expect(githubLink).toBeInTheDocument();
    expect(githubLink).toHaveAttribute('href', 'https://github.com/andrew-aromin');
  });

  it('renders Resume link with correct href and label', () => {
    renderHeader();
    const resumeLink = screen.getByRole('link', { name: /resume/i });
    expect(resumeLink).toBeInTheDocument();
    expect(resumeLink).toHaveAttribute('href', '/resume.pdf');
  });
});
