import { defineStore } from 'pinia'

interface UserState {
  name: string
  gender: string
  birthday: string
  birthTime: string
  focusArea: string
  leftHandImage: string | null // 这将存储本地预览 URL 或服务器返回的文件名
  rightHandImage: string | null
  leftHandFile: File | null // 新增：存储原始文件对象，不持久化
  rightHandFile: File | null // 新增：存储原始文件对象，不持久化
  cardCode: string
  location: string
  mbti: string
  calendarType: 'gregorian' | 'lunar'
  zodiac: string
  bazi: string
  baziFavorableElements: string
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    name: '',
    gender: '女',
    birthday: '',
    birthTime: '12:00',
    focusArea: '情感姻缘',
    leftHandImage: null,
    rightHandImage: null,
    leftHandFile: null,
    rightHandFile: null,
    cardCode: '',
    location: '',
    mbti: '',
    calendarType: 'gregorian',
    zodiac: '',
    bazi: '',
    baziFavorableElements: ''
  }),
  actions: {
    setUserInfo(info: Partial<UserState>) {
      Object.assign(this.$state, info)
    },
    reset() {
      this.$reset()
    }
  }
})
