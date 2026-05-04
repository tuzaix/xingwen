import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  // 提取基础域名，去掉 /api/v1 路径
  const apiBaseUrl = env.VITE_API_BASE_URL || '/api/v1'
  // 如果是相对路径，代理到本地后端；如果是绝对路径，提取域名
  const proxyTarget = apiBaseUrl.startsWith('http') 
    ? apiBaseUrl.replace(/\/api\/v1\/?$/, '')
    : 'http://127.0.0.1:8641'

  return {
    base: '/admin/',
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
