<template>
  <div class="min-h-screen bg-slate-900 text-white p-6 flex flex-col relative overflow-hidden">
    <!-- Background Decoration -->
    <div class="absolute bottom-[-5%] left-[-5%] w-48 h-48 bg-purple-500/10 rounded-full blur-3xl"></div>

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
        <div class="w-8 h-1 rounded-full bg-slate-700"></div>
      </div>
      <div class="w-10"></div>
    </div>

    <div class="flex-1 relative z-10">
      <div class="text-center mb-10">
        <h2 class="text-3xl font-serif font-bold mb-3 text-amber-200">✨ 让星辰认识你 ✨</h2>
        <p class="text-slate-400 text-sm">准确的信息将帮助 AI 提供更精准的解析</p>
      </div>

      <div class="space-y-8">
        <!-- 1 & 2. 姓名与性别 (在一行展示) -->
        <div class="grid grid-cols-5 gap-4">
          <div class="col-span-3 form-item">
            <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">
              您的姓名 <span class="text-amber-500">*</span>
            </label>
            <input
              v-model="form.name"
              type="text"
              placeholder="请输入姓名"
              class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-5 focus:border-amber-500/50 outline-none transition-all text-white placeholder:text-slate-600"
            />
          </div>

          <div class="col-span-2 form-item">
            <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">
              您的性别 <span class="text-amber-500">*</span>
            </label>
            <div class="flex gap-2">
              <button
                v-for="g in ['男', '女']"
                :key="g"
                @click="form.gender = g"
                class="flex-1 py-4 rounded-xl border transition-all font-bold text-sm"
                :class="form.gender === g ? 'border-amber-500 bg-amber-500/10 text-amber-400' : 'border-slate-700 bg-slate-800/50 text-slate-500'"
              >
                {{ g }}
              </button>
            </div>
          </div>
        </div>

        <!-- 3. 出生日期 -->
        <div class="form-item">
          <div class="flex items-center justify-between mb-3">
            <label class="block text-xs font-bold text-amber-500/50 uppercase tracking-widest">
              出生日期 <span class="text-amber-500">*</span>
            </label>
            <div class="flex gap-2">
              <button
                v-for="type in [{label: '公历', value: 'gregorian'}, {label: '农历', value: 'lunar'}]"
                :key="type.value"
                @click="handleCalendarTypeChange(type.value as 'gregorian' | 'lunar')"
                class="px-4 py-1.5 rounded-full text-xs font-bold transition-all border"
                :class="form.calendarType === type.value ? 'bg-amber-500 border-amber-500 text-slate-900' : 'bg-transparent border-slate-700 text-slate-500'"
              >
                {{ type.label }}
              </button>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <!-- Year -->
            <div class="relative">
              <select
                v-model="birthDate.year"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-sm"
              >
                <option v-for="y in years" :key="y" :value="y">{{ y }}年</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <!-- Month -->
            <div class="relative">
              <select
                v-model="birthDate.month"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-sm"
              >
                <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <!-- Day -->
            <div class="relative">
              <select
                v-model="birthDate.day"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-sm"
              >
                <option v-for="d in daysInMonth" :key="d" :value="d">{{ d }}日</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. 出生时间 -->
        <div class="form-item">
          <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">出生时间</label>
          <div class="flex gap-3 h-[56px]">
            <div v-if="form.birthTime !== ''" class="flex-1 grid grid-cols-2 gap-2 h-full">
              <!-- Hour -->
              <div class="relative h-full">
                <select
                  v-model="birthTimeState.hour"
                  class="w-full h-full bg-slate-800/50 border border-slate-700 rounded-xl px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-sm"
                >
                  <option v-for="h in 24" :key="h-1" :value="(h-1).toString().padStart(2, '0')">{{ (h-1).toString().padStart(2, '0') }}时</option>
                </select>
                <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              <!-- Minute -->
              <div class="relative h-full">
                <select
                  v-model="birthTimeState.minute"
                  class="w-full h-full bg-slate-800/50 border border-slate-700 rounded-xl px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-sm"
                >
                  <option v-for="m in 60" :key="m-1" :value="(m-1).toString().padStart(2, '0')">{{ (m-1).toString().padStart(2, '0') }}分</option>
                </select>
                <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
            <div v-else class="flex-1 h-full bg-slate-800/30 border border-dashed border-slate-700 rounded-xl px-4 text-slate-500 text-xs flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>时间未知，将以正午估算</span>
            </div>
            <button
              @click="toggleBirthTime"
              class="px-6 h-full rounded-xl font-bold transition-all border shrink-0 text-sm"
              :class="form.birthTime === '' ? 'bg-amber-500 border-amber-500 text-slate-900' : 'bg-transparent border-slate-700 text-slate-500'"
            >
              未知
            </button>
          </div>
        </div>

        <!-- 5. 出生地 -->
        <div class="form-item">
          <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">
            您的出生地 <span class="text-amber-500">*</span>
          </label>
          <div class="grid grid-cols-3 gap-2">
            <div class="relative">
              <select
                v-model="birthPlaceState.province"
                @change="handleBirthProvinceChange"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-xs"
              >
                <option value="">省份</option>
                <option v-for="p in cityData" :key="p.name" :value="p.name">{{ p.name }}</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <div class="relative">
              <select
                v-model="birthPlaceState.city"
                @change="handleBirthCityChange"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-xs"
                :disabled="!birthPlaceState.province"
              >
                <option value="">城市</option>
                <option v-for="c in birthAvailableCities" :key="c.name" :value="c.name">{{ c.name }}</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <div class="relative">
              <select
                v-model="birthPlaceState.district"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-xs"
                :disabled="!birthPlaceState.city"
              >
                <option value="">区/县</option>
                <option v-for="d in birthAvailableDistricts" :key="d.name" :value="d.name">{{ d.name }}</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- 6. 所在城市 -->
        <div class="form-item">
          <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">
            当前所在城市 <span class="text-amber-500">*</span>
          </label>
          <div class="grid grid-cols-3 gap-2 mb-2">
            <!-- Province -->
            <div class="relative">
              <select
                v-model="locationState.province"
                @change="handleProvinceChange"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-xs"
              >
                <option value="">省份</option>
                <option v-for="p in cityData" :key="p.name" :value="p.name">{{ p.name }}</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <!-- City -->
            <div class="relative">
              <select
                v-model="locationState.city"
                @change="handleCityChange"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-xs"
                :disabled="!locationState.province"
              >
                <option value="">城市</option>
                <option v-for="c in availableCities" :key="c.name" :value="c.name">{{ c.name }}</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
            <!-- District -->
            <div class="relative">
              <select
                v-model="locationState.district"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-3 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-xs"
                :disabled="!locationState.city"
              >
                <option value="">区/县</option>
                <option v-for="d in availableDistricts" :key="d.name" :value="d.name">{{ d.name }}</option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
          <button 
            @click="getLocation"
            class="flex items-center gap-1 text-[10px] text-amber-500/60 hover:text-amber-500 transition-colors ml-1"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            使用当前位置快速填充
          </button>
        </div>

        <!-- 6 & 7. 星座与 MBTI (在一行展示) -->
        <div class="grid grid-cols-2 gap-4">
          <div class="form-item">
            <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">
              您的星座 <span class="text-amber-500">*</span>
            </label>
            <div class="relative">
              <select
                v-model="form.zodiac"
                class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-5 focus:border-amber-500/50 outline-none transition-all text-white appearance-none text-sm"
              >
                <option value="" disabled>请选择星座</option>
                <option v-for="z in zodiacs" :key="z" :value="z">{{ z }}</option>
              </select>
              <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

          <div class="form-item">
            <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">MBTI 类型 (可选)</label>
            <input
              v-model="form.mbti"
              type="text"
              placeholder="例如：INTJ"
              class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-5 focus:border-amber-500/50 outline-none transition-all text-white placeholder:text-slate-600"
            />
          </div>
        </div>

        <!-- 8. 此刻最想探寻的方向与心念 -->
        <div class="form-item">
          <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">
            此刻最想探寻的方向 <span class="text-amber-500">*</span>
          </label>
          <div class="grid grid-cols-2 gap-3 mb-4">
            <button
              v-for="area in areas"
              :key="area"
              @click="form.focusArea = area"
              class="py-3 px-2 rounded-xl border text-sm transition-all font-bold"
              :class="form.focusArea === area ? 'border-amber-500 bg-amber-500/10 text-amber-400' : 'border-slate-700 bg-slate-800/50 text-slate-500'"
            >
              {{ area }}
            </button>
          </div>
          
          <label class="block text-xs font-bold text-amber-500/50 mb-3 uppercase tracking-widest">
            求测心念 (选择或输入您的困惑)
          </label>
          
          <!-- 预设选项 -->
          <div class="flex flex-wrap gap-2 mb-4">
            <button
              v-for="opt in intentionOptions"
              :key="opt"
              @click="selectIntention(opt)"
              class="px-3 py-2 rounded-lg border text-[11px] transition-all"
              :class="form.coreIntention === opt ? 'border-amber-500 bg-amber-500/10 text-amber-400' : 'border-slate-700 bg-slate-800/30 text-slate-500'"
            >
              {{ opt }}
            </button>
          </div>

          <textarea
            v-model="form.coreIntention"
            placeholder="也可在此直接描述您的具体困惑..."
            rows="3"
            class="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-4 px-5 focus:border-amber-500/50 outline-none transition-all text-white placeholder:text-slate-600 text-sm resize-none"
          ></textarea>
        </div>
      </div>
    </div>

    <div class="mt-8 pb-8 relative z-10">
      <button
        @click="nextStep"
        :disabled="!isFormValid"
        class="w-full py-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2"
        :class="isFormValid 
          ? 'bg-gradient-to-r from-amber-400 to-amber-600 text-slate-900 shadow-[0_0_20px_rgba(251,191,36,0.2)]' 
          : 'bg-slate-800 text-slate-500 cursor-not-allowed'"
      >
        下一步：上传手相
        <svg v-if="isFormValid" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import cityData from '../assets/city-data.json'
import { Solar, Lunar } from 'lunar-javascript'

const router = useRouter()
const userStore = useUserStore()

const areas = ['情感姻缘', '事业发展', '财富运势', '自我成长']
const zodiacs = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']

// 预设的核心诉求选项
const intentionOptions = computed(() => {
  const options: Record<string, string[]> = {
    '情感姻缘': ['何时遇到正缘？', '对方是否值得托付？', '近期感情会有波动吗？', '如何修复当前关系？'],
    '事业发展': ['近期有升职加薪机会吗？', '现在适合跳槽吗？', '创业前景如何？', '职场人际关系怎么处理？'],
    '财富运势': ['财运什么时候爆发？', '适合进行大额投资吗？', '会有意外之财吗？', '如何守住现有财富？'],
    '自我成长': ['我的天赋潜能在哪里？', '如何克服性格弱点？', '目前的状态该如何突破？', '未来的发展重心在哪？'],
    '综合运势': ['未来三个月的整体运势', '今年的关键转折点', '需要注意的风险和机遇', '提升运势的有效方法']
  }
  return options[form.focusArea] || options['综合运势']
})

const selectIntention = (option: string) => {
  form.coreIntention = option
}

const handleCalendarTypeChange = (newType: 'gregorian' | 'lunar') => {
  if (form.calendarType === newType) return

  const { year, month, day } = birthDate
  
  try {
    if (newType === 'lunar') {
      // From Solar to Lunar
      const solar = Solar.fromYmd(year, month, day)
      const lunar = solar.getLunar()
      birthDate.year = lunar.getYear()
      birthDate.month = lunar.getMonth()
      birthDate.day = lunar.getDay()
    } else {
      // From Lunar to Solar
      const lunar = Lunar.fromYmd(year, month, day)
      const solar = lunar.getSolar()
      birthDate.year = solar.getYear()
      birthDate.month = solar.getMonth()
      birthDate.day = solar.getDay()
    }
  } catch (e) {
    console.error('Calendar conversion error:', e)
  }
  
  form.calendarType = newType
}

// Location Logic
const locationState = reactive({
  province: '',
  city: '',
  district: ''
})

const birthPlaceState = reactive({
  province: '',
  city: '',
  district: ''
})

onMounted(() => {
  calculateZodiac()
  if (userStore.location) {
    const parts = userStore.location.split(' ')
    if (parts.length >= 3) {
      locationState.province = parts[0]
      locationState.city = parts[1]
      locationState.district = parts[2]
    }
  }
  if (userStore.birthPlace) {
    const parts = userStore.birthPlace.split(' ')
    if (parts.length >= 3) {
      birthPlaceState.province = parts[0]
      birthPlaceState.city = parts[1]
      birthPlaceState.district = parts[2]
    }
  }
})

const getCities = (provinceName: string) => {
  const p = cityData.find(p => p.name === provinceName)
  return p ? p.children : []
}

const getDistricts = (provinceName: string, cityName: string) => {
  const cities = getCities(provinceName)
  const c = cities.find(c => c.name === cityName)
  return c ? c.children : []
}

const availableCities = computed(() => getCities(locationState.province))
const availableDistricts = computed(() => getDistricts(locationState.province, locationState.city))

const birthAvailableCities = computed(() => getCities(birthPlaceState.province))
const birthAvailableDistricts = computed(() => getDistricts(birthPlaceState.province, birthPlaceState.city))

const handleProvinceChange = () => {
  locationState.city = ''
  locationState.district = ''
}

const handleCityChange = () => {
  locationState.district = ''
}

const handleBirthProvinceChange = () => {
  birthPlaceState.city = ''
  birthPlaceState.district = ''
}

const handleBirthCityChange = () => {
  birthPlaceState.district = ''
}

// Split date logic
const currentYear = new Date().getFullYear()
const years = Array.from({ length: 100 }, (_, i) => currentYear - i)

// Initial date parsing
const parseInitialDate = () => {
  if (userStore.birthday) {
    const d = new Date(userStore.birthday)
    if (!isNaN(d.getTime())) return d
  }
  return new Date(1995, 0, 1)
}

const initialDate = parseInitialDate()
const birthDate = reactive({
  year: initialDate.getFullYear(),
  month: initialDate.getMonth() + 1,
  day: initialDate.getDate()
})

// Birth Time State
const birthTimeState = reactive({
  hour: userStore.birthTime ? userStore.birthTime.split(':')[0] : '12',
  minute: userStore.birthTime ? userStore.birthTime.split(':')[1] : '00'
})

const toggleBirthTime = () => {
  if (form.birthTime === '') {
    form.birthTime = `${birthTimeState.hour}:${birthTimeState.minute}`
  } else {
    form.birthTime = ''
  }
}

const daysInMonth = computed(() => {
  if (form.calendarType === 'lunar') {
    // In lunar-javascript, a lunar month has either 29 or 30 days.
    // We can try to create a lunar date with 30, if it's invalid it's 29.
    try {
      Lunar.fromYmd(birthDate.year, birthDate.month, 30)
      return 30
    } catch (e) {
      return 29
    }
  }
  return new Date(birthDate.year, birthDate.month, 0).getDate()
})

// Ensure day is valid when month/year changes
watch([() => birthDate.year, () => birthDate.month], () => {
  if (birthDate.day > daysInMonth.value) {
    birthDate.day = daysInMonth.value
  }
})

const form = reactive({
  name: userStore.name,
  gender: userStore.gender || '女',
  birthday: userStore.birthday,
  birthTime: userStore.birthTime || '',
  birthPlace: userStore.birthPlace,
  focusArea: userStore.focusArea || '综合运势',
  coreIntention: userStore.coreIntention || '',
  location: userStore.location,
  mbti: userStore.mbti,
  calendarType: userStore.calendarType || 'gregorian',
  zodiac: userStore.zodiac,
  bazi: '',
  baziFavorableElements: ''
})

const calculateZodiac = () => {
  if (!form.birthday) return
  
  const [year, month, day] = form.birthday.split('-').map(Number)
  if (!year || !month || !day) return

  let solar: Solar
  if (form.calendarType === 'lunar') {
    const lunar = Lunar.fromYmd(year, month, day)
    solar = lunar.getSolar()
  } else {
    solar = Solar.fromYmd(year, month, day)
  }
  
  form.zodiac = solar.getXingZuo() + '座'

  // 计算八字和喜用神
  try {
    const [hour, minute] = form.birthTime.split(':').map(Number)
    let baziSolar: Solar
    if (form.calendarType === 'lunar') {
      const lunar = Lunar.fromYmdHms(year, month, day, hour || 0, minute || 0, 0)
      baziSolar = lunar.getSolar()
    } else {
      baziSolar = Solar.fromYmdHms(year, month, day, hour || 0, minute || 0, 0)
    }
    
    const eightChar = baziSolar.getLunar().getEightChar()
    form.bazi = `${eightChar.getYear()}年 ${eightChar.getMonth()}月 ${eightChar.getDay()}日 ${eightChar.getTime()}时`
    form.baziFavorableElements = `五行分布：${eightChar.getYearWuXing()} ${eightChar.getMonthWuXing()} ${eightChar.getDayWuXing()} ${eightChar.getTimeWuXing()}`
  } catch (e) {
    console.error('Bazi calculation error:', e)
  }
}

watch([() => form.birthday, () => form.birthTime, () => form.calendarType], () => {
  calculateZodiac()
})

const getLocation = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((position) => {
      // In a real app, you would use reverse geocoding to get province/city/district
      // For this demo, we'll just set it to a fixed location if they allow it
      console.log('Location:', position.coords.latitude, position.coords.longitude)
      locationState.province = '北京市'
      locationState.city = '北京市'
      locationState.district = '朝阳区'
    }, (err) => {
      console.error('Geolocation error:', err)
    })
  }
}

// Watch locationState to update form.location
watch(locationState, (newVal) => {
  if (newVal.province && newVal.city && newVal.district) {
    form.location = `${newVal.province} ${newVal.city} ${newVal.district}`
  } else {
    form.location = ''
  }
})

// Watch birthPlaceState to update form.birthPlace
watch(birthPlaceState, (newVal) => {
  if (newVal.province && newVal.city && newVal.district) {
    form.birthPlace = `${newVal.province} ${newVal.city} ${newVal.district}`
  } else {
    form.birthPlace = ''
  }
})

// Sync birthDate to form.birthday
watch(birthDate, (newVal) => {
  const y = newVal.year
  const m = newVal.month.toString().padStart(2, '0')
  const d = newVal.day.toString().padStart(2, '0')
  form.birthday = `${y}-${m}-${d}`
}, { immediate: true })

// Sync birthTimeState to form.birthTime
watch(birthTimeState, (newVal) => {
  if (form.birthTime !== '') {
    form.birthTime = `${newVal.hour}:${newVal.minute}`
  }
})

const isFormValid = computed(() => {
  return form.name.trim() !== '' && 
         form.birthday !== '' && 
         form.location !== '' && 
         form.birthPlace !== '' &&
         form.zodiac !== '' &&
         form.coreIntention.trim() !== ''
})

const nextStep = () => {
  if (isFormValid.value) {
    userStore.setUserInfo(form)
    userStore.zodiac = form.zodiac
    router.push('/verify')
  }
}
</script>
