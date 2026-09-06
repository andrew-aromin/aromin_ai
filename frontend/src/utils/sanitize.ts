import DOMPurify from 'dompurify';

/**
 * Sanitizes user input on the frontend using DOMPurify.
 * Strips all HTML tags and attributes for plain-text inputs to prevent XSS.
 * Defense-in-depth sanitization also occurs on the backend.
 */
export const sanitizeFrontendInput = (input: string): string => {
  if (!input) return '';

  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
  }).trim();
};
