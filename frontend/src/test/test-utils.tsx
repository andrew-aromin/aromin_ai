import type { ReactElement } from 'react';
import type { RenderOptions } from '@testing-library/react';
import { render } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';

export function renderWithMantine(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(<MantineProvider defaultColorScheme="dark">{ui}</MantineProvider>, options);
}

export * from '@testing-library/react';
