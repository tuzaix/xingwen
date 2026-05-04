<template>
  <div class="min-h-screen bg-slate-900 text-white p-6 flex flex-col relative overflow-hidden">
    <!-- Background Decoration -->
    <div class="absolute top-[-10%] left-[-10%] w-64 h-64 bg-amber-500/10 rounded-full blur-3xl"></div>

    <div class="flex items-center justify-between mb-8 relative z-10">
      <button @click="$router.back()" class="p-2 -ml-2 text-slate-400 hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="flex gap-1">
        <div class="w-8 h-1 rounded-full bg-amber-500"></div>
        <div class="w-8 h-1 rounded-full bg-amber-500"></div>
        <div class="w-8 h-1 rounded-full bg-amber-500"></div>
        <div class="w-8 h-1 rounded-full bg-amber-500"></div>
      </div>
      <div class="w-10"></div>
    </div>

    <div class="flex-1 flex flex-col items-center relative z-10">
      <div class="text-center mb-10">
        <h2 class="text-3xl font-serif font-bold mb-3 text-amber-200">🔑 验证专属卡密</h2>
        <p class="text-slate-400 text-sm">卡密是开启星辰解析的唯一密钥</p>
      </div>

      <div class="w-full max-w-sm space-y-6">
        <div class="relative">
          <input
            v-model="cardCode"
            type="text"
            maxlength="19"
            placeholder="XW-XXXX-XXXX-XXXX"
            @input="formatCardCode"
            class="w-full bg-slate-800/50 border border-slate-700 rounded-2xl py-6 px-4 text-2xl font-mono tracking-widest text-center focus:border-amber-500/50 outline-none transition-all text-amber-400"
            :class="{ 'border-red-500/50': errorMsg, 'border-green-500/50': isValidated }"
          />
          <div class="absolute -bottom-6 left-0 right-0 text-center">
            <span v-if="errorMsg" class="text-red-400 text-xs font-light">✕ {{ errorMsg }}</span>
            <span v-if="isValidated" class="text-green-400 text-xs font-light">✓ 验证通过，密钥有效</span>
          </div>
        </div>

        <div class="pt-8">
          <div class="bg-amber-500/5 border border-amber-500/10 rounded-xl p-4 text-xs text-amber-100/60 leading-relaxed">
            <p class="flex items-start gap-2">
              <span class="text-amber-500">◈</span>
              <span>单次卡密仅限生成一份深度解析报告。</span>
            </p>
            <p class="flex items-start gap-2 mt-2">
              <span class="text-amber-500">◈</span>
              <span>如需获取卡密，请关注官方公众号或点击下方链接。</span>
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-8 pb-8 relative z-10">
      <button
        @click="startAnalysis"
        :disabled="!isValidated || loading"
        class="w-full py-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2"
        :class="isValidated 
          ? 'bg-gradient-to-r from-amber-400 to-amber-600 text-slate-900 shadow-[0_0_20px_rgba(251,191,36,0.2)]' 
          : 'bg-slate-800 text-slate-500 cursor-not-allowed'"
      >
        <svg v-if="loading" class="animate-spin h-5 w-5 text-slate-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>{{ loading ? '正在校验...' : '开启星辰解析' }}</span>
      </button>
      
      <p class="text-center mt-6 text-xs text-amber-500/60 underline tracking-widest">
        如何获取卡密？
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

const cardCode = ref(userStore.cardCode)
const loading = ref(false)
const errorMsg = ref('')
const isValidated = ref(false)

const formatCardCode = (e: Event) => {
  let val = (e.target as HTMLInputElement).value.toUpperCase().replace(/[^A-Z0-9]/g, '')
  let formatted = ''
  for (let i = 0; i < val.length && i < 16; i++) {
    if (i > 0 && i % 4 === 0) formatted += '-'
    formatted += val[i]
  }
  cardCode.value = formatted
  errorMsg.value = ''
  isValidated.value = false
}

watch(cardCode, async (newVal) => {
  const pureCode = newVal.replace(/-/g, '')
  if (pureCode.length === 16) {
    await validateCard(newVal)
  }
})

const validateCard = async (code: string) => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await axios.post('/card/verify', { card_code: code }, {
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
    })
    if (res.data.valid) {
      isValidated.value = true
      userStore.setUserInfo({ cardCode: code })
    } else if (res.data.report_id) {
      // 已经使用过，直接跳转到结果页
      isValidated.value = true
      userStore.setUserInfo({ cardCode: code })
      alert('该卡密已使用，正在为您跳转至之前的解析报告')
      router.replace(`/report/${res.data.report_id}`)
    } else {
      errorMsg.value = res.data.message || '卡密无效或已被使用'
    }
  } catch (error: any) {
    errorMsg.value = error.response?.data?.detail || '卡密无效或已被使用'
  } finally {
    loading.value = false
  }
}

const startAnalysis = () => {
  if (isValidated.value) {
    router.replace('/report/loading')
  }
}
</script>
