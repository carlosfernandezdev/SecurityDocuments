import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    cors: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8002",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://127.0.0.1:8002",
        ws: true,
        changeOrigin: true,
      },
      "/health": {
        target: "http://127.0.0.1:8002",
        changeOrigin: true,
      },
    },
  },
});
