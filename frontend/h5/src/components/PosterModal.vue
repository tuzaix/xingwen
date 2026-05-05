<template>
  <Transition name="fade">
    <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/90 backdrop-blur-sm">
      <div class="relative w-full max-w-sm animate-scale-in">
        <!-- Close Button -->
        <button 
          @click="close" 
          class="absolute -top-12 right-0 p-2 text-slate-400 hover:text-white transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- Loading State -->
        <div v-if="generating" class="bg-slate-900 rounded-3xl p-12 flex flex-col items-center justify-center border border-slate-800">
          <div class="w-12 h-12 border-4 border-amber-500/20 border-t-amber-500 rounded-full animate-spin mb-4"></div>
          <p class="text-amber-200/80 font-serif tracking-widest">星辰绘卷生成中...</p>
        </div>

        <!-- Generated Image -->
        <div v-else class="relative group">
          <img :src="posterUrl" class="w-full rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-white/10" alt="Share Poster" />
          
          <div class="absolute inset-x-0 -bottom-16 flex flex-col items-center gap-2">
            <p class="text-amber-200/60 text-[10px] tracking-[0.2em] uppercase font-light">长按上方图片保存至相册</p>
            <div class="flex gap-2">
              <div class="w-1 h-1 rounded-full bg-amber-500/20"></div>
              <div class="w-1 h-1 rounded-full bg-amber-500/40"></div>
              <div class="w-1 h-1 rounded-full bg-amber-500/20"></div>
            </div>
          </div>
        </div>

        <!-- Hidden DOM to be captured by html2canvas -->
        <div 
          ref="posterSource"
          class="poster-capture-container absolute pointer-events-none bg-[#020617] text-white overflow-hidden font-serif"
          style="width: 375px; height: 667px; left: -9999px; top: 0;"
        >
          <div class="relative p-8 h-full flex flex-col w-[375px] bg-[#020617]">
            <!-- Simplified Background -->
            <div class="absolute inset-0 bg-gradient-to-b from-slate-900 to-black"></div>
            
            <!-- Minimal CSS Stars -->
            <div class="absolute inset-0 overflow-hidden opacity-30">
              <div v-for="n in 30" :key="n" 
                class="absolute bg-white rounded-full"
                :style="{
                  width: '2px',
                  height: '2px',
                  top: ((n * 17) % 100) + '%',
                  left: ((n * 23) % 100) + '%'
                }"
              ></div>
            </div>

            <div class="absolute top-0 right-0 w-48 h-48 bg-amber-500/10 rounded-full blur-3xl"></div>

            <div class="relative z-10 flex-1 flex flex-col">
              <!-- Header -->
              <div class="flex items-center justify-between mb-8">
                <div class="w-12 h-12 rounded-xl bg-amber-500 flex items-center justify-center overflow-hidden">
                  <span class="text-black text-4xl font-bold leading-none -translate-y-4">星</span>
                </div>
                <div class="text-right">
                  <p class="text-amber-200 text-[14px] tracking-widest leading-tight">每一道掌纹</p>
                  <p class="text-amber-200 text-[14px] tracking-widest leading-tight">都是星辰的轨迹</p>
                  <p class="text-amber-500/60 text-[10px] tracking-[0.3em] uppercase leading-tight">Deep Soul Analysis</p>
                </div>
              </div>

              <!-- Title -->
              <div class="mb-10 text-center">
                <h1 class="text-2xl font-bold text-amber-200 mb-2 leading-snug tracking-[0.3em]">
                  星纹 · 全息解析
                </h1>
                <div class="h-px w-24 mx-auto bg-amber-500/30"></div>
              </div>

              <!-- User Info -->
              <div class="bg-white/5 rounded-2xl p-6 border border-white/10 mb-8">
                <div class="flex items-center gap-4 mb-4">
                  <div class="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-2xl border border-amber-500/30 overflow-hidden">
                    <span class="leading-none -translate-y-2.5">{{ gender === '男' ? '🧔' : '👩' }}</span>
                  </div>
                  <div class="flex flex-col justify-center">
                    <h2 class="text-xl font-bold text-amber-100 leading-none">{{ maskedName }}</h2>
                  </div>
                </div>
                <div class="flex flex-wrap gap-2">
                  <!-- 标签整体向上微调，保持视觉重心 -->
                  <span v-for="tag in tags" :key="tag" class="px-2 py-1.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400/80 text-[10px] leading-none flex items-center">
                    <span class="-translate-y-1.5"># {{ tag }}</span>
                  </span>
                </div>
              </div>

              <!-- Summary Quote -->
              <div class="flex-1 px-6 relative flex items-center justify-center">
                <div class="absolute left-0 top-0 text-5xl text-amber-500/10 font-serif">“</div>
                <p class="text-slate-200 text-base leading-relaxed italic text-center relative z-10 px-2 font-light">
                  {{ summary }}
                </p>
                <div class="absolute right-0 bottom-0 text-5xl text-amber-500/10 font-serif rotate-180">“</div>
              </div>

              <!-- Footer -->
              <div class="mt-12 pt-8 border-t border-white/5 flex items-center justify-center">
                <div class="text-center">
                  <p class="text-amber-500/40 text-[8px] uppercase tracking-[0.4em]">Xingwen AI · Destiny Analysis</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import html2canvas from 'html2canvas'

const props = defineProps<{
  show: boolean
  name: string
  gender: string
  birthday: string
  reportContent: string
  sections?: any[]
}>()

const emit = defineEmits(['update:show'])

const generating = ref(true)
const posterUrl = ref('')
const posterSource = ref<HTMLElement | null>(null)
const summary = ref('')
const tags = ref(['先天格', '后天运', '星辰指引'])

// 名字隐私处理
const maskedName = computed(() => {
  if (!props.name) return ''
  const str = props.name.trim()
  const len = str.length
  if (len <= 1) return str
  if (len === 2) return str[0] + '*'
  return str[0] + '*' + str[len - 1]
})

const close = () => {
  emit('update:show', false)
}

const extractSummary = (content: string) => {
  if (!content) return '星辰已为您指引方向，命格深处蕴含着无限可能。'
  
  // 查找“结语：星辰的祝福”或类似的关键词
  const keywords = ['结语：星辰的祝福', '结语', '星辰的祝福']
  let summaryText = ''
  
  for (const kw of keywords) {
    const idx = content.indexOf(kw)
    if (idx !== -1) {
      // 截取关键词之后的内容
      summaryText = content.substring(idx + kw.length).trim()
      break
    }
  }
  
  // 如果没找到结语，回退到原始逻辑（取第一段）
  if (!summaryText) {
    const cleanContent = content.replace(/[#*`]/g, '').trim()
    const sentences = cleanContent.split(/[。！？\n]/).filter(s => s.length > 5)
    summaryText = sentences[0] || '星辰已为您指引方向，命格深处蕴含着无限可能。'
  }
  
  // 清理 Markdown 符号并限制长度
  summaryText = summaryText.replace(/[#*`]/g, '').trim()
  
  // 如果内容太长，适当截断以保证海报美观
  if (summaryText.length > 120) {
    return summaryText.substring(0, 115) + '...'
  }
  return summaryText
}

watch(() => props.show, async (newVal) => {
  if (newVal) {
    generating.value = true
    
    // 尝试从附录文案中随机挑选一条
    let rawSummary = ''
    const shareCopySection = props.sections?.find(s => s.chapter_id === 'share_copy' || s.chapter_title?.includes('分享文案') || s.chapter_title?.includes('附录'))
    
    if (shareCopySection && shareCopySection.paragraphs?.length > 0) {
      console.log('Found share_copy section, picking random paragraph')
      const paragraphs = shareCopySection.paragraphs
      rawSummary = paragraphs[Math.floor(Math.random() * paragraphs.length)]
      
      // 限制分享文案长度，确保海报美观
      if (rawSummary.length > 150) {
        rawSummary = rawSummary.substring(0, 145) + '...'
      }
    } else if (props.reportContent) {
      // 兜底逻辑：从报告正文中提取
      rawSummary = extractSummary(props.reportContent)
    } else {
      rawSummary = '星辰已为您指引方向，命格深处蕴含着无限可能。'
    }

    // 对 summary 中的人名进行脱敏处理
    if (props.name && rawSummary.includes(props.name)) {
      rawSummary = rawSummary.split(props.name).join(maskedName.value)
    }
    summary.value = rawSummary
    
    console.log('Generating poster with summary:', summary.value)
    
    // Wait for Vue to update the DOM
    await nextTick()
    
    // Additional wait for images and styles
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (posterSource.value) {
      try {
        console.log('Capturing element:', posterSource.value)
        const canvas = await html2canvas(posterSource.value, {
          useCORS: true,
          scale: 2,
          backgroundColor: '#020617',
          logging: true, // Enable logging to debug
          width: 375,
          height: 667,
          onclone: (clonedDoc) => {
            const el = clonedDoc.querySelector('.poster-capture-container') as HTMLElement
            if (el) {
              el.style.left = '0'
              el.style.top = '0'
              el.style.position = 'relative'
              el.style.visibility = 'visible'
              el.style.opacity = '1'
              el.style.display = 'block'
              el.style.zIndex = '10000'
              
              // Ensure child visibility
              const children = el.querySelectorAll('*')
              children.forEach(child => {
                if (child instanceof HTMLElement) {
                  child.style.visibility = 'visible'
                  child.style.opacity = '1'
                }
              })
            }
          }
        })
        
        posterUrl.value = canvas.toDataURL('image/png')
        console.log('Poster generated successfully')
        generating.value = false
      } catch (err) {
        console.error('Failed to generate poster:', err)
        generating.value = false
      }
    } else {
      console.error('posterSource.value is null')
      generating.value = false
    }
  }
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.animate-scale-in {
  animation: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

/* Ensure font-serif works on capture */
.font-serif {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
}
</style>
