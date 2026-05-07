<template>
  <div class="home-container h-screen flex flex-col justify-between p-6 bg-slate-900 text-white overflow-hidden relative">
    <!-- Background Decoration -->
    <div class="absolute top-[-10%] left-[-10%] w-64 h-64 bg-purple-600/20 rounded-full blur-3xl"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-64 h-64 bg-blue-600/20 rounded-full blur-3xl"></div>

    <div class="flex-1 flex flex-col justify-center items-center relative z-10">
      <div class="w-32 h-32 mb-8 animate-pulse">
        <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="90" stroke="currentColor" stroke-width="2" class="text-amber-400" />
          <path d="M60 100C60 77.9086 77.9086 60 100 60C122.091 60 140 77.9086 140 100M60 100C60 122.091 77.9086 140 100 140C122.091 140 140 122.091 140 100M60 100H140M100 60V140" stroke="currentColor" stroke-width="1" class="text-amber-400/50" />
          <circle cx="100" cy="100" r="10" fill="currentColor" class="text-amber-400" />
        </svg>
      </div>
      
      <h1 class="text-5xl font-serif font-bold mb-4 tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-amber-200 to-amber-500">
        星纹 AI
      </h1>
      <p class="text-xl text-amber-100/80 font-light mb-2">每一道掌纹，都是星辰的轨迹</p>
      <div class="h-1 w-12 bg-amber-400/50 rounded-full mb-8"></div>
      
      <div class="space-y-4 text-center text-sm text-slate-400 font-light max-w-[280px]">
        <p>融合千年东方相学与现代视觉 AI 技术</p>
        <p>为您解析生命中潜藏的无限可能</p>
      </div>
    </div>

    <div class="pb-12 relative z-10">
      <router-link 
        to="/upload" 
        class="block w-full py-4 text-center bg-gradient-to-r from-amber-400 to-amber-600 text-slate-900 font-bold rounded-xl shadow-[0_0_20px_rgba(251,191,36,0.3)] hover:scale-[1.02] transition-transform active:scale-[0.98]"
      >
        开始探索掌纹
      </router-link>
      <p class="text-center mt-4 text-xs text-slate-500">
        已有 12,849 位用户开启了星辰之旅
      </p>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
}
</style>
