import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      host: true,
      proxy: {
        '/api': {
          target: env.VITE_NODE_API_PROXY_TARGET || 'http://localhost:5000',
          changeOrigin: true,
        },
        '/python-api': {
          target: env.VITE_PYTHON_API_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/python-api/, ''),
        },
      },
    },
  }
})
