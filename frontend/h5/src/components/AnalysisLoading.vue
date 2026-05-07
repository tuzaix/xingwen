<template>
  <div class="loading-overlay fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-900 overflow-hidden">
    <!-- Background Space Effect -->
    <div class="absolute inset-0 opacity-30">
      <div v-for="i in 50" :key="i" 
           class="absolute bg-white rounded-full"
           :style="{
             width: Math.random() * 3 + 'px',
             height: Math.random() * 3 + 'px',
             top: Math.random() * 100 + '%',
             left: Math.random() * 100 + '%',
             animation: `twinkle ${Math.random() * 3 + 2}s infinite ${Math.random() * 5}s`
           }">
      </div>
    </div>

    <div class="star-container relative w-72 h-72 mb-16">
      <!-- Animated orbits -->
      <div class="orbit orbit-1 border-amber-500/20"></div>
      <div class="orbit orbit-2 border-blue-500/20"></div>
      <div class="orbit orbit-3 border-purple-500/20"></div>
      
      <!-- Rotating planet-like elements -->
      <div class="planet planet-1 bg-amber-400"></div>
      <div class="planet planet-2 bg-blue-400"></div>
      
      <!-- Center energy ball -->
      <div class="energy-core absolute inset-0 m-auto w-20 h-20 rounded-full bg-gradient-to-br from-amber-300 to-amber-600 shadow-[0_0_50px_rgba(251,191,36,0.5)] flex items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.382-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
      </div>
    </div>

    <div class="text-center px-8 relative z-10 w-full max-w-xs">
      <h3 class="text-2xl font-serif font-bold mb-6 text-amber-200 tracking-widest">星辰感应中</h3>
      
      <div class="relative h-1.5 w-full bg-slate-800 rounded-full overflow-hidden mb-6 shadow-inner">
        <div 
          class="h-full bg-gradient-to-r from-amber-500 to-amber-300 transition-all duration-700 ease-out shadow-[0_0_10px_rgba(251,191,36,0.5)]" 
          :style="{ width: displayProgress + '%' }"
        ></div>
      </div>
      
      <div class="h-6 overflow-hidden">
        <transition name="slide-up" mode="out-in">
          <p :key="currentText" class="text-amber-500/80 text-sm font-light italic tracking-wider">
            {{ currentText }}
          </p>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  progress?: number
  statusText?: string
}>()

const displayProgress = ref(0)
const currentText = ref('正在连接阿卡西记录...')
const texts = [
  '正在连接阿卡西记录...',
  '正在读取先天命格数据...',
  '正在扫描双手镜像特征...',
  '正在进行时空交叉比对...',
  '正在计算地磁场匹配度...',
  '正在同步星辰能量轨迹...',
  '正在解析生辰八字磁场...',
  '正在汇聚全息推演结果...',
  '正在撰写深度命理报告...',
  '天机即将显现...'
]

const ritualTexts = [
  '星辰指引已现，正在整合天机...',
  '命理画卷已绘就，正在加盖星印...',
  '正在同步现实维度，请稍候...',
  '万事俱备，开启命运之门...'
]

let textInterval: any
let fakeProgressInterval: any
let ritualIndex = 0

onMounted(() => {
  let textIndex = 0
  textInterval = setInterval(() => {
    if (props.progress === 100) {
      // 当报告生成完成进入仪式延迟阶段，使用特殊的收尾文案
      currentText.value = ritualTexts[ritualIndex % ritualTexts.length]
      ritualIndex++
    } else if (!props.statusText) {
      textIndex = (textIndex + 1) % texts.length
      currentText.value = texts[textIndex]
    } else {
      currentText.value = props.statusText
    }
  }, 2500)

  fakeProgressInterval = setInterval(() => {
    if (props.progress !== undefined) {
      // If we have real progress, move displayProgress towards it
      if (displayProgress.value < props.progress) {
        displayProgress.value += 1
      }
    } else {
      // Fake progress
      if (displayProgress.value < 95) {
        displayProgress.value += Math.random() * 2
      }
    }
  }, 200)
})

onUnmounted(() => {
  clearInterval(textInterval)
  clearInterval(fakeProgressInterval)
})
</script>

<style scoped>
.orbit {
  position: absolute;
  top: 50%;
  left: 50%;
  border: 1px solid;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.orbit-1 { width: 100%; height: 100%; animation: spin 12s linear infinite; }
.orbit-2 { width: 75%; height: 75%; animation: spin 8s linear reverse infinite; }
.orbit-3 { width: 50%; height: 50%; animation: spin 5s linear infinite; }

.planet {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  top: 0;
  left: 50%;
  margin-left: -6px;
  margin-top: -6px;
  box-shadow: 0 0 10px currentColor;
}

.planet-1 { 
  top: 50%; left: 0; 
  animation: orbit-1 12s linear infinite;
}

.planet-2 { 
  top: 12.5%; left: 87.5%; 
  animation: orbit-2 8s linear infinite;
}

@keyframes spin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

.energy-core {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 30px rgba(251,191,36,0.3); }
  50% { transform: scale(1.05); box-shadow: 0 0 60px rgba(251,191,36,0.6); }
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.5s ease;
}
.slide-up-enter-from { opacity: 0; transform: translateY(10px); }
.slide-up-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
