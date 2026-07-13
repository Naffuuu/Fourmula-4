import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/setupTests.js",
  },
  server: {
    port: 5173,
    proxy: {
      // Anything the frontend calls under /api during dev is forwarded to FastAPI,
      // so the browser never needs to know the backend's real host/port.
      "/api": {
        target: process.env.VITE_API_PROXY_TARGET || "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: process.env.VITE_WS_PROXY_TARGET || "ws://localhost:8000",
        ws: true,
      },
    },
  },
});
