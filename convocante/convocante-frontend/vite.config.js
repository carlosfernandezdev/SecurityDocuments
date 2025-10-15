import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Ajusta el proxy si quieres evitar CORS en dev
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    // proxy: { '/convocante': 'http://127.0.0.1:8001' }
  }
})
