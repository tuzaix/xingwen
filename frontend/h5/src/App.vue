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
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from './stores/user'

const route = useRoute()
const userStore = useUserStore()

const updateCardCode = (code: any) => {
  if (code) {
    userStore.setUserInfo({ cardCode: (code as string).toUpperCase() })
  }
}

onMounted(() => {
  updateCardCode(route.query.card_code)
})

// 持续监听路由参数变化，确保卡密实时同步到 store
watch(() => route.query.card_code, (newVal) => {
  updateCardCode(newVal)
})
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
