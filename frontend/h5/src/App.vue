<template>
  <div class="min-h-screen bg-gray-950 flex justify-center">
    <!-- 移动端优先的响应式容器 -->
    <div class="w-full max-w-md bg-slate-900 shadow-2xl min-h-screen relative overflow-x-hidden border-x border-slate-800">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const lastCheckedCode = ref('')

const updateCardCode = async (code: any) => {
  if (!code) return
  
  const formattedCode = (code as string).toUpperCase().replace(/[^A-Z0-9]/g, '')
  if (formattedCode.length === 16) {
    // 只有当卡密变化时才检查，避免循环或重复检查
    if (formattedCode === lastCheckedCode.value) return
    lastCheckedCode.value = formattedCode
    
    // 同步到 store
    userStore.setUserInfo({ cardCode: formattedCode })
    
    // 检查卡密是否已使用
    try {
      const res = await axios.post('/card/verify', { card_code: formattedCode }, {
        baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1'
      })
      
      if (res.data.report_id) {
        // 已使用，且当前不在该报告页，则跳转
        if (route.name !== 'report' || route.params.id !== res.data.report_id) {
          console.log('Card code used, redirecting to report:', res.data.report_id)
          router.replace(`/report/${res.data.report_id}`)
        }
      }
    } catch (error) {
      console.error('Verify card code failed:', error)
    }
  } else if (formattedCode) {
    userStore.setUserInfo({ cardCode: formattedCode })
  }
}

onMounted(() => {
  if (route.query.card_code) {
    updateCardCode(route.query.card_code)
  }
})

// 持续监听路由参数变化，确保卡密实时同步到 store 并检查状态
watch(() => route.query.card_code, (newVal) => {
  updateCardCode(newVal)
}, { immediate: true })
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 全局滚动条美化 */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(251, 191, 36, 0.1);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(251, 191, 36, 0.3);
}
</style>
