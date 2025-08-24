// Polyfills for older browsers and compatibility
import regeneratorRuntime from 'regenerator-runtime/runtime'

// Global polyfill for regeneratorRuntime
if (typeof global === 'undefined') {
  window.global = window
}

// Ensure regeneratorRuntime is available globally
if (typeof window !== 'undefined' && !window.regeneratorRuntime) {
  window.regeneratorRuntime = regeneratorRuntime
}
