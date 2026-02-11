import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Resolve ~@ibm/plex paths used by Carbon
      '~@ibm/plex': path.resolve(__dirname, 'node_modules/@ibm/plex'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // Use environment variable or default to Fyre VM
        target: process.env.VITE_API_URL || 'http://9.30.147.112:8000',
        changeOrigin: true,
      },
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        quietDeps: true,
      },
    },
  },
})
