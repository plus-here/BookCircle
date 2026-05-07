import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'

let https
if (process.env.VITE_HTTPS_PFX) {
  https = {
    pfx: fs.readFileSync(process.env.VITE_HTTPS_PFX),
    passphrase: process.env.VITE_HTTPS_PFX_PASSPHRASE || "",
  }
} else if (process.env.VITE_HTTPS_CERT && process.env.VITE_HTTPS_KEY) {
  https = {
    cert: fs.readFileSync(process.env.VITE_HTTPS_CERT),
    key: fs.readFileSync(process.env.VITE_HTTPS_KEY),
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    https,
    headers: {
      "Cache-Control": "no-store, max-age=0",
    },
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://127.0.0.1:8001",
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
