import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'

let https
if (process.env.VITE_HTTPS_PFX) {
  https = {
    pfx: fs.readFileSync(process.env.VITE_HTTPS_PFX),
    passphrase: process.env.VITE_HTTPS_PFX_PASSPHRASE || "",
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    https,
  },
})
