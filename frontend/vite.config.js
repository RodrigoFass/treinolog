import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    // Em desenvolvimento o Vite repassa /api para a API Flask (evita CORS)
    proxy: {
      '/api': 'http://127.0.0.1:5000',
    },
  },
})
