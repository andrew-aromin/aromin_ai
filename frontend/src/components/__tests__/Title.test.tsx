import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Title from '../Title';

describe('Title Component', () => {
  it('renders the title text correctly', () => {
    render(<Title />);
    const titleText = screen.getByText(/Hi, I'm Andrew./i);
    expect(titleText).toBeInTheDocument();
  });

  it('renders the avatar image correctly', () => {
    render(<Title />);
    const avatarImage = screen.getByAltText('Andrew Aromin');
    expect(avatarImage).toHaveAttribute('src', '/avatar.png');
  });

  it('renders the description text correctly', () => {
    render(<Title />);
    const descriptionText = screen.getByText(
      /Built using React, FastAPI, and Ollama/i
    );
    expect(descriptionText).toBeInTheDocument();
  });
});