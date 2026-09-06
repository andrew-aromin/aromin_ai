import '@testing-library/jest-dom/vitest';

// Polyfill window.matchMedia for Mantine components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Polyfill ResizeObserver for Mantine ScrollArea
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = ResizeObserverMock;

// Polyfill document.fonts for Mantine Textarea Autosize
if (typeof document !== 'undefined') {
  Object.defineProperty(document, 'fonts', {
    writable: true,
    value: {
      addEventListener: () => {},
      removeEventListener: () => {},
      ready: Promise.resolve(),
    },
  });
}

// Polyfill scrollIntoView
window.HTMLElement.prototype.scrollIntoView = function () {};
