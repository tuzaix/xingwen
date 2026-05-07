<template>
  <div class="min-h-screen bg-slate-900 text-white p-6 flex flex-col relative overflow-hidden">
    <!-- Background Decoration -->
    <div class="absolute top-[-10%] left-[-10%] w-64 h-64 bg-amber-500/10 rounded-full blur-3xl"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-64 h-64 bg-blue-500/10 rounded-full blur-3xl"></div>

    <div class="flex items-center justify-between mb-8 relative z-10">
      <button @click="$router.back()" class="p-2 -ml-2 text-slate-400 hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="flex gap-1">
        <div class="w-8 h-1 rounded-full bg-amber-500"></div>
        <div class="w-8 h-1 rounded-full bg-slate-700"></div>
        <div class="w-8 h-1 rounded-full bg-slate-700"></div>
        <div class="w-8 h-1 rounded-full bg-slate-700"></div>
      </div>
      <div class="w-10"></div>
    </div>

    <div class="flex-1 flex flex-col relative z-10">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-serif font-bold mb-3 text-amber-200">上传手相照片</h2>
        <p class="text-slate-400 text-sm tracking-widest uppercase">左手定先天 · 右手定后天</p>
      </div>

      <div class="flex flex-col gap-4">
        <div class="grid grid-cols-2 gap-4">
          <!-- Left Hand -->
          <div class="space-y-3">
            <div class="flex items-center gap-2 px-1">
              <span class="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></span>
              <span class="text-[14px] font-bold text-amber-500/80 uppercase tracking-widest">左手(先天)</span>
            </div>
            <ImageUpload
              title="拍摄左手"
              subtitle="清晰对焦"
              side="left"
              :initialImage="userStore.leftHandImage"
              @upload="(file, preview) => handleUpload('left', file, preview)"
              @clear="() => handleClear('left')"
            />
          </div>

          <!-- Right Hand -->
          <div class="space-y-3">
            <div class="flex items-center gap-2 px-1">
              <span class="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></span>
              <span class="text-[14px] font-bold text-blue-400/80 uppercase tracking-widest">右手(后天)</span>
            </div>
            <ImageUpload
              title="拍摄右手"
              subtitle="均匀光线"
              side="right"
              :initialImage="userStore.rightHandImage"
              @upload="(file, preview) => handleUpload('right', file, preview)"
              @clear="() => handleClear('right')"
            />
          </div>
        </div>

        <!-- Shooting Tips -->
        <div class="mt-16 grid grid-cols-3 gap-8 px-2">
          <div class="flex flex-col items-center text-center">
            <div class="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mb-4 text-amber-400/90 text-2xl shadow-xl border border-slate-700/50">💡</div>
            <p class="text-sm text-slate-200 leading-relaxed font-bold tracking-wide">光线充足<br/>避免阴影</p>
          </div>
          <div class="flex flex-col items-center text-center">
            <div class="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mb-4 text-amber-400/90 text-2xl shadow-xl border border-slate-700/50">✋</div>
            <p class="text-sm text-slate-200 leading-relaxed font-bold tracking-wide">手掌平展<br/>五指分开</p>
          </div>
          <div class="flex flex-col items-center text-center">
            <div class="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mb-4 text-amber-400/90 text-2xl shadow-xl border border-slate-700/50">🔍</div>
            <p class="text-sm text-slate-200 leading-relaxed font-bold tracking-wide">对焦准确<br/>掌纹清晰</p>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-8 pb-8 relative z-10">
      <button
        @click="nextStep"
        :disabled="!isReady || uploading"
        class="w-full py-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2"
        :class="isReady && !uploading
          ? 'bg-gradient-to-r from-amber-400 to-amber-600 text-slate-900 shadow-[0_0_20px_rgba(251,191,36,0.2)]' 
          : 'bg-slate-800 text-slate-500 cursor-not-allowed'"
      >
        <template v-if="uploading">
          <svg class="animate-spin h-5 w-5 text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          正在同步星象...
        </template>
        <template v-else>
          {{ isReady ? '下一步：填写信息' : '请先上传双掌照片' }}
          <svg v-if="isReady" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </template>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import ImageUpload from '../components/ImageUpload.vue'

const router = useRouter()
const userStore = useUserStore()
const loadingLeft = ref(false)
const loadingRight = ref(false)

const uploading = computed(() => loadingLeft.value || loadingRight.value)

const isReady = computed(() => {
  return userStore.leftHandImage && userStore.rightHandImage
})

const handleUpload = (side: 'left' | 'right', file: File, preview: string) => {
  if (side === 'left') {
    userStore.setUserInfo({ 
      leftHandImage: preview, 
      leftHandFile: file 
    })
  } else {
    userStore.setUserInfo({ 
      rightHandImage: preview, 
      rightHandFile: file 
    })
  }
}

const handleClear = (side: 'left' | 'right') => {
  if (side === 'left') {
    userStore.setUserInfo({ leftHandImage: null, leftHandFile: null })
  } else {
    userStore.setUserInfo({ rightHandImage: null, rightHandFile: null })
  }
}

const nextStep = () => {
  if (isReady.value) {
    router.push('/info')
  }
}
</script>
