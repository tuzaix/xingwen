import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  // 提取基础域名，去掉 /api/v1 路径
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
  const proxyTarget = apiBaseUrl.replace(/\/api\/v1\/?$/, '')

  return {
    plugins: [vue()],
    server: {
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
        '/uploads': {
          target: proxyTarget,
          changeOrigin: true,
        }
      }
    }
  }
})
