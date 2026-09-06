import { describe, it, expect } from 'vitest';
import { sanitizeFrontendInput } from '../sanitize';

describe('sanitizeFrontendInput', () => {
  it('returns empty string for empty or whitespace input', () => {
    expect(sanitizeFrontendInput('')).toBe('');
    expect(sanitizeFrontendInput('   ')).toBe('');
  });

  it('returns trimmed plain text unchanged', () => {
    expect(sanitizeFrontendInput('Hello world')).toBe('Hello world');
    expect(sanitizeFrontendInput('  What is your experience?  ')).toBe('What is your experience?');
  });

  it('strips script tags and executable javascript', () => {
    const malicious = "<script>alert('XSS')</script>";
    expect(sanitizeFrontendInput(malicious)).toBe('');
  });

  it('strips html tags while preserving plain text', () => {
    const input = '<b>Bold</b> and <i>italic</i>';
    expect(sanitizeFrontendInput(input)).toBe('Bold and italic');
  });

  it('strips dangerous event handlers', () => {
    const input = '<img src="x" onerror="alert(1)" />Text';
    expect(sanitizeFrontendInput(input)).toBe('Text');
  });
});
