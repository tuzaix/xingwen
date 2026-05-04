import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000 // Increase to 30s
})

service.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    console.log(`Sending request to ${config.url}`, {
      hasToken: !!authStore.token,
      method: config.method
    })
    if (authStore.token) {
      config.headers['Authorization'] = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('Response error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    })
    
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
      ElMessage.error('会话已过期，请重新登录')
    } else {
      ElMessage.error(error.response?.data?.detail || '网络请求失败，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default service
