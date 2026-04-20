import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/api': {
                target: 'https://team-pass.ycalk.tech',
                changeOrigin: true,
                secure: true,
            }
        }
    }
})