import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Force rebuild by changing build config
    minify: 'terser',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  server: {
    host: true,
    port: 5173,
    proxy: process.env.NODE_ENV === 'production' ? undefined : {
      '/api': {
        target: 'http://127.0.0.1:5007',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  define: {
    __APP_VERSION__: '"2025-04-25-19-00-ROLES-FIX"'
  }
})
