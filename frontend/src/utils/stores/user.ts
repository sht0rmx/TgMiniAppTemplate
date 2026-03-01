import { defineStore } from 'pinia'

export interface UserData {
  id: string
  telegram_id: number
  username: string | null
  name: string
  role: string
  avatar_url: string | null
  last_seen: string
  created_at: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    data: null as UserData | null,
  }),
  actions: {
    setUser(user: UserData) {
      this.data = user
    },
    clearUser() {
      this.data = null
    }
  }
})