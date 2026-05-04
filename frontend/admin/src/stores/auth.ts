import { defineStore } from 'pinia'

interface AuthState {
  token: string | null
  userInfo: {
    username: string
    realName: string
    role: string
  } | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    userInfo: null
  }),
  actions: {
    setToken(token: string) {
      this.token = token
    },
    setUserInfo(info: any) {
      this.userInfo = info
    },
    logout() {
      this.token = null
      this.userInfo = null
    }
  },
  persist: true
})
