// frontend/src/components/TypingIndicator.test.tsx

import React from 'react';
import { render } from '@testing-library/react';
import TypingIndicator from './TypingIndicator';

describe('TypingIndicator', () => {
  it('renders the Avatar with Cpu icon', () => {
    const { getByRole, getByTestId } = render(<TypingIndicator />);
    
    // Check if Avatar is rendered
    const avatar = getByRole('img');
    expect(avatar).toBeInTheDocument();
    
    // Check if Cpu icon is rendered inside Avatar
    const cpuIcon = getByTestId('cpu-icon');
    expect(cpuIcon).toBeInTheDocument();
  });

  it('renders three typing dots', () => {
    const { getAllByClassName } = render(<TypingIndicator />);
    
    // Check if there are exactly three typing dots
    const typingDots = getAllByClassName('typing-dot');
    expect(typingDots).toHaveLength(3);
  });
});