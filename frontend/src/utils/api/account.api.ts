import apiClientInst from './api.ts'
import { AuthService } from './auth.api.ts'

export interface LinkTokenResponse {
  token: string
}

export class AccountService {
  private static ACCOUNT_BASE = '/api/v1/account'
  static async getTelegramLinkingToken(): Promise<string | null> {
    try {
      const res = await apiClientInst.post(`${this.ACCOUNT_BASE}/link/telegram/token`, {})
      if (res.status === 200 && res.data.token) {
        return res.data.token
      }
      return null
    } catch (error) {
      console.error('Error getting Telegram linking token:', error)
      return null
    }
  }
  static async linkTelegram(initData: string): Promise<boolean> {
    try {
      const res = await apiClientInst.post(`${this.ACCOUNT_BASE}/link/telegram`, {
        initData,
      })
      return res.status === 200
    } catch (error) {
      console.error('Error linking Telegram:', error)
      return false
    }
  }
  static async linkYandex(code: string): Promise<boolean> {
    try {
      const res = await apiClientInst.post(`${this.ACCOUNT_BASE}/link/yandex`, {
        code,
      })
      return res.status === 200
    } catch (error) {
      console.error('Error linking Yandex:', error)
      return false
    }
  }

  static async unlinkAccount(provider: 'telegram' | 'yandex'): Promise<boolean> {
    try {
      const res = await apiClientInst.post(
        `${this.ACCOUNT_BASE}/unlink/${provider}`,
        {}
      )
      return res.status === 200
    } catch (error) {
      console.error(`Error unlinking ${provider}:`, error)
      return false
    }
  }

  static async deleteAccount(): Promise<boolean> {
    try {
      const res = await apiClientInst.delete(`${this.ACCOUNT_BASE}`)
      return res.status === 200
    } catch (error) {
      console.error('Error deleting account:', error)
      return false
    }
  }
}
