const normalizeBase = (value, fallback = '') => {
  const base = value ?? fallback
  return base.replace(/\/$/, '')
}

export const nodeApiBase = normalizeBase(import.meta.env.VITE_NODE_API_BASE_URL, '')
export const pythonApiBase = normalizeBase(import.meta.env.VITE_PYTHON_API_BASE_URL, '/python-api')
