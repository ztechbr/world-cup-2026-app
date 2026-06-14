import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://ai-worldcup26.jd0rwz.easypanel.host',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        headers: {
          'X-Token': 'COPA26!'
        }
      },
      '/stats': {
        target: 'http://localhost:90',
        changeOrigin: true,
        ws: true
      }
    }
  }
});
