import '@testing-library/jest-dom'

// O ResponsiveContainer do Recharts depende de ResizeObserver, ausente no jsdom.
class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

globalThis.ResizeObserver = globalThis.ResizeObserver ?? (ResizeObserverStub as unknown as typeof ResizeObserver)
