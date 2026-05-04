<template>
  <div class="login-container">
    <div class="login-card-wrapper">
      <div class="login-header">
        <div class="logo-circle">
          <img src="../assets/vue.svg" alt="logo" />
        </div>
        <h2>星纹 AI 管理系统</h2>
        <p>Master Control Panel</p>
      </div>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-position="top" class="login-form">
        <el-form-item label="管理员账号" prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入账号" 
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item label="登录密码" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码" 
            :prefix-icon="Lock" 
            show-password 
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item class="mt-8">
          <el-button type="primary" class="login-button" :loading="loading" @click="handleLogin">
            立即登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        &copy; 2024 Xingwen AI. All rights reserved.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import request from '../utils/request'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('username', loginForm.username)
        formData.append('password', loginForm.password)
        
        const res: any = await request.post('/auth/login', formData)
        authStore.setToken(res.access_token)
        authStore.setUserInfo({ username: loginForm.username, realName: '管理员', role: 'super_admin' })
        
        router.push('/')
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, #1e293b 0%, #0f172a 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  width: 150%;
  height: 150%;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2394a3b8' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2v-4h4v-2h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2v-4h4v-2H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
  animation: moveBackground 60s linear infinite;
}

@keyframes moveBackground {
  from { transform: translate(0, 0); }
  to { transform: translate(-60px, -60px); }
}

.login-card-wrapper {
  width: 420px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  padding: 40px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  z-index: 10;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-circle {
  width: 64px;
  height: 64px;
  background: #fbbf24;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 0 20px rgba(251, 191, 36, 0.3);
}

.logo-circle img {
  width: 32px;
  height: 32px;
}

.login-header h2 {
  color: #f8fafc;
  font-size: 24px;
  margin: 0;
  font-weight: 700;
  letter-spacing: 1px;
}

.login-header p {
  color: #94a3b8;
  font-size: 14px;
  margin: 8px 0 0;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.login-form :deep(.el-form-item__label) {
  color: #94a3b8;
  font-weight: 500;
  padding-bottom: 8px;
}

.login-form :deep(.el-input__wrapper) {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none !important;
  border-radius: 12px;
  padding: 4px 12px;
}

.login-form :deep(.el-input__inner) {
  color: #f8fafc;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: #475569;
}

.login-button {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: #fbbf24;
  border: none;
  color: #0f172a;
  transition: all 0.3s;
}

.login-button:hover {
  background: #f59e0b;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(251, 191, 36, 0.4);
}

.login-footer {
  text-align: center;
  margin-top: 40px;
  color: #475569;
  font-size: 12px;
}

.mt-8 {
  margin-top: 32px;
}
</style>
