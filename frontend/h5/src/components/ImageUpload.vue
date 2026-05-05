<template>
  <div class="upload-component w-full">
    <div
      class="upload-area border-2 border-dashed border-amber-500/30 rounded-2xl flex flex-col items-center justify-center bg-slate-800/50 backdrop-blur-md relative overflow-hidden group aspect-[3/4] w-full"
      @click="triggerFileSelect"
    >
      <div class="absolute inset-0 bg-amber-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
      
      <template v-if="!previewUrl">
        <!-- Hand Guide Overlay -->
        <div class="absolute inset-0 flex items-center justify-center p-8 pointer-events-none opacity-30">
          <svg 
            viewBox="0 0 24 24" 
            class="w-full h-full text-amber-500"
            :class="{ 'scale-x-[-1]': side === 'right' }"
            fill="none" 
            stroke="currentColor" 
            stroke-width="0.5" 
            stroke-dasharray="2 2"
          >
            <path d="M7 11.5V6a2 2 0 0 1 2-2 2 2 0 0 1 2 2v5.5m0 0V5a2 2 0 0 1 2-2 2 2 0 0 1 2 2v6.5m0 0V7a2 2 0 0 1 2-2 2 2 0 0 1 2 2v9a5 5 0 0 1-5 5H9.7a5 5 0 0 1-4.7-3.2L3.5 12" />
          </svg>
        </div>

        <div class="flex flex-col items-center justify-center p-4 relative z-10">
          <div class="w-12 h-12 mb-3 flex items-center justify-center bg-amber-500/10 rounded-full text-amber-400 group-hover:scale-110 transition-transform">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <p class="text-amber-100/90 text-sm font-medium mb-1">{{ title }}</p>
          <p class="text-amber-500/70 text-[10px] italic">{{ subtitle }}</p>
        </div>
      </template>
      <template v-else>
        <div class="absolute inset-0 w-full h-full">
          <img :src="previewUrl" class="w-full h-full object-cover" :class="{ 'opacity-40 grayscale': loading }" />
          <div class="absolute inset-0 bg-black/20"></div>
          
          <!-- Loading Overlay -->
          <div v-if="loading" class="absolute inset-0 flex flex-col items-center justify-center">
            <svg class="animate-spin h-8 w-8 text-amber-500 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span class="text-[10px] text-amber-200 font-bold tracking-widest uppercase">同步中...</span>
          </div>

          <button 
            v-else
            class="absolute bottom-3 right-3 bg-black/40 backdrop-blur-md text-white text-[10px] px-3 py-1 rounded-full border border-white/10"
            @click.stop="handleClear"
          >
            重新拍摄
          </button>
        </div>
      </template>
    </div>
    
    <input
      type="file"
      ref="fileInput"
      class="hidden"
      accept="image/*"
      @change="onFileChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  title: string
  subtitle: string
  initialImage?: string | null
  loading?: boolean
  side?: 'left' | 'right'
}>()

const emit = defineEmits(['upload', 'clear'])

const fileInput = ref<HTMLInputElement | null>(null)
const previewUrl = ref(props.initialImage || '')

watch(() => props.initialImage, (newVal) => {
  if (newVal) {
    previewUrl.value = newVal
  } else {
    previewUrl.value = ''
  }
})

const triggerFileSelect = () => {
  fileInput.value?.click()
}

const handleClear = () => {
  previewUrl.value = ''
  emit('clear')
}

const onFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (event) => {
      previewUrl.value = event.target?.result as string
      emit('upload', file, previewUrl.value)
    }
    reader.readAsDataURL(file)
  }
}
</script>

<style scoped>
.upload-area {
  transition: all 0.3s ease;
}
.upload-area:active {
  transform: scale(0.98);
}
</style>
