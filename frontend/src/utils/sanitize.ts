import DOMPurify from 'dompurify';

/**
 * Sanitizes user input on the frontend using DOMPurify.
 * This removes potentially malicious HTML and scripts to prevent XSS.
 * Note: Comprehensive sanitization also occurs on the backend for defense-in-depth.
 */
export const sanitizeFrontendInput = (input: string): string => {
  if (!input) return '';

  // Clean the input and trim whitespace
  return DOMPurify.sanitize(input, {
    USE_PROFILES: { html: true },
    ALLOWED_TAGS: [], // For plain text inputs, we strip all tags
    ALLOWED_ATTR: [],
  }).trim();
};
