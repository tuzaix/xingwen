<template>
  <el-container class="admin-layout">
    <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar-container">
      <div class="logo-container" :class="{ 'collapsed': isCollapse }">
        <img src="../assets/vue.svg" alt="logo" class="logo" />
        <span v-if="!isCollapse" class="logo-text">星纹 AI 后台</span>
      </div>
      
      <el-menu
        :collapse="isCollapse"
        :default-active="activeMenu"
        background-color="#1e293b"
        text-color="#94a3b8"
        active-text-color="#fbbf24"
        class="sidebar-menu"
        router
      >
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <el-menu-item index="/cards">
          <el-icon><Ticket /></el-icon>
          <template #title>卡密管理</template>
        </el-menu-item>
        
        <el-menu-item index="/reports">
          <el-icon><Files /></el-icon>
          <template #title>报告管理</template>
        </el-menu-item>
        
        <el-menu-item index="/stats">
          <el-icon><PieChart /></el-icon>
          <template #title>数据统计</template>
        </el-menu-item>
        
        <el-menu-item index="/config">
          <el-icon><Operation /></el-icon>
          <template #title>系统配置</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer" v-if="!isCollapse">
        <div class="logout-btn" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          <span>退出登录</span>
        </div>
      </div>
      <div class="sidebar-footer collapsed" v-else>
        <el-tooltip content="退出登录" placement="right">
          <el-icon class="logout-icon" @click="handleLogout"><SwitchButton /></el-icon>
        </el-tooltip>
      </div>
    </el-aside>

    <el-container class="main-container">
      <el-header class="admin-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.name !== 'dashboard'">{{ pageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" class="avatar">管</el-avatar>
              <span class="username">系统管理员</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="admin-main">
        <div class="page-content">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
      
      <el-footer class="admin-footer">
        © 2024 星纹 AI 手相命理解析系统 · 版权所有
      </el-footer>
    </el-container>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordVisible"
      title="修改管理员密码"
      width="400px"
      append-to-body
      destroy-on-close
      @closed="resetPasswordForm"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-position="top"
      >
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="passwordVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitPasswordChange">确定修改</el-button>
        </div>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessageBox, ElMessage, type FormInstance } from 'element-plus'
import request from '../utils/request'
import { 
  DataBoard, 
  Ticket, 
  Files, 
  PieChart, 
  Operation, 
  Expand, 
  Fold, 
  ArrowDown,
  SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    'dashboard': '控制台',
    'cards': '卡密管理',
    'reports': '报告管理',
    'stats': '数据统计',
    'config': '系统配置'
  }
  return titles[route.name as string] || ''
})

// 修改密码相关
const passwordVisible = ref(false)
const submitting = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }]
}

const handleCommand = (command: string) => {
  console.log('Dropdown command:', command)
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'password') {
    console.log('Opening password dialog')
    passwordVisible.value = true
  }
}

const resetPasswordForm = () => {
  passwordFormRef.value?.resetFields()
}

const submitPasswordChange = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await request.post('/auth/change-password', {
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password
        })
        ElMessage.success('密码修改成功，请重新登录')
        passwordVisible.value = false
        // 强制重新登录
        setTimeout(() => {
          authStore.logout()
          router.push('/login')
        }, 1500)
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '修改失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    buttonSize: 'default'
  }).then(() => {
    authStore.logout()
    router.push('/login')
  })
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.sidebar-container {
  background-color: #1e293b;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  height: 100%;
  border-right: none;
}

.logo-container {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: #0f172a;
  overflow: hidden;
  transition: all 0.3s;
}

.logo-container.collapsed {
  justify-content: center;
  padding: 0;
}

.logo {
  width: 32px;
  height: 32px;
}

.logo-text {
  color: #f8fafc;
  font-weight: 700;
  font-size: 18px;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 54px;
  line-height: 54px;
  margin: 4px 12px;
  border-radius: 8px;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #334155 !important;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.sidebar-footer {
  margin-top: auto;
  padding: 16px;
  border-top: 1px solid #334155;
}

.sidebar-footer.collapsed {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-radius: 8px;
  color: #f87171;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.logout-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.logout-icon {
  font-size: 20px;
  color: #f87171;
  cursor: pointer;
  transition: color 0.3s;
}

.logout-icon:hover {
  color: #ef4444;
}

.main-container {
  background-color: #f1f5f9;
  display: flex;
  flex-direction: column;
}

.admin-header {
  background-color: #fff;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #64748b;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: #fbbf24;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f8fafc;
}

.username {
  font-size: 14px;
  color: #334155;
  font-weight: 500;
}

.avatar {
  background-color: #fbbf24;
  color: #fff;
  font-weight: bold;
}

.admin-main {
  padding: 24px;
  overflow-y: auto;
}

.page-content {
  max-width: 1600px;
  margin: 0 auto;
}

.admin-footer {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 12px;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

/* Transitions */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
