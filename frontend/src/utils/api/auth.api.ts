import { useUserStore } from '@/utils/stores/user.ts'
import apiClientInst, { apiClient, type EmptyResponse } from './api.ts'
import router from '@/utils/router.ts'
import { authStatus } from '@/main.ts'

const API_URL = import.meta.env.VITE_API_URL as string
const FRONT_URL = import.meta.env.VITE_FRONTEND_URL as string

export interface WebAppLoginRequest {
  initData: string
}

export interface YandexLoginRequest {
  code: string
}

export interface RecoveryResponse {
  code: string
  detail?: string
}

export interface RecoveryRequest {
  recovery_code: string
}

export interface AccessResponse {
  access_token: string
  recovery_code?: string
  detail?: string
}

export class AuthService {
  private static AUTH_BASE = '/api/v1/auth'
  static async webappLogin(data: WebAppLoginRequest): Promise<AccessResponse | null> {
    const res = await apiClientInst.post(`${this.AUTH_BASE}/login/webapp`, data)
    if (res.status === 200) {
      apiClient.setAccessToken(res.data.access_token)
      return res.data
    }
    return null
  }

  static async yandexLogin(data: YandexLoginRequest): Promise<AccessResponse | null> {
    try {
      const res = await apiClientInst.post(`${this.AUTH_BASE}/login/yandex`, data)
      if (res.status === 200) {
        apiClient.setAccessToken(res.data.access_token)
        return res.data
      }
      return null
    } catch (error) {
      console.error('Yandex login error:', error)
      return null
    }
  }

  static async transferAccount(data: RecoveryRequest): Promise<boolean> {
    try {
      const res = await apiClientInst.post(`${this.AUTH_BASE}/token/transfer`, data)
      return res.status === 200
    } catch (error) {
      console.error('Transfer error:', error)
      return false
    }
  }

  static async startQrLogin() {
    const res = await apiClientInst.get(`${this.AUTH_BASE}/login/getqr`)

    if (res.status !== 200 || !res.data.login_id) {
      throw new Error('Failed to retrieve login ID from server.')
    }

    const loginId = res.data.login_id
    const loginCode = res.data.code as string
    const base64Params = btoa(loginId)

    const qrUrl = `${FRONT_URL}accept?loginid=${base64Params}`

    const result = await this.startSseConfirmation(loginId)

    return {
      loginId,
      loginCode,
      qrUrl,
      authPromise: result.authPromise,
      cancelSse: result.cancel,
    }
  }

  static async startSseConfirmation(loginId: string) {
    let evtSource: any = null

    const cancel = () => {
      if (evtSource) {
        console.log('SSE connection manually closed.')
        evtSource.close()
        evtSource = null
      }
    }

    const connect = (loginId: string) => {
      return new Promise((resolve, reject) => {
        const url = `${API_URL}api/v1/auth/sse/check/${loginId}`

        try {
          evtSource = new EventSource(url)
        } catch (error) {
          console.log(error)
          reject(new Error('EventSource initialization failed.'))
          return
        }

        evtSource.onmessage = (event: any) => {
          const data = JSON.parse(event.data)
          if (data.type === 'auth_success' && data.access_token) {
            cancel()
            resolve(data.access_token)
            apiClient.setAccessToken(data.access_token)
          } else if (data.type === 'auth_denied' || data.type === 'timeout') {
            cancel()
            reject(new Error(data.message || 'Login denied or timed out.'))
          }
        }

        evtSource.onerror = (err: any) => {
          console.error('SSE error, attempting reconnect:', err)
          cancel()

          setTimeout(() => {
            connect(loginId).then(resolve).catch(reject)
          }, 1000)
        }
      })
    }

    return { authPromise: connect(loginId), cancel }
  }

  static async checkLogin(loginId: string): Promise<boolean> {
    const resp = await apiClientInst.get(`${this.AUTH_BASE}/login/search/${loginId}`)
    if (resp.status !== 200) {
      return false
    }
    return true
  }

  static async validateLogin(loginId: string): Promise<boolean> {
    const resp = await apiClientInst.get(`${this.AUTH_BASE}/login/accept/${loginId}`)
    if (resp.status !== 200) {
      return false
    }
    return true
  }

  static async searchByCode(code: string): Promise<boolean> {
    try {
      const resp = await apiClientInst.get(`${this.AUTH_BASE}/login/code/search/${code}`)
      return resp.status === 200
    } catch {
      return false
    }
  }

  static async acceptByCode(code: string): Promise<boolean> {
    try {
      const resp = await apiClientInst.get(`${this.AUTH_BASE}/login/code/accept/${code}`)
      return resp.status === 200
    } catch {
      return false
    }
  }

  static async check(): Promise<boolean> {
    const store = useUserStore()
    const res = await apiClientInst.get(`${this.AUTH_BASE}/check`)

    if (!res || res.status !== 200) {
      store.clearUser()
      authStatus.value = false
      await router.push('/login')
      return false
    }
    store.setUser(res.data.user)
    authStatus.value = true
    return true
  }

  static async recreateTokens(): Promise<boolean> {
    try {
      const resp = await apiClientInst.get(`${this.AUTH_BASE}/token/recreate-tokens`)
      if (resp.status == 200) {
        let data: AccessResponse = resp.data
        apiClient.setAccessToken(data.access_token)
        return true
      }
      return false
    } catch (e) {
      return false
    }
  }

  static async revokeRefreshSession(): Promise<boolean> {
    const resp = await apiClientInst.get(`${this.AUTH_BASE}/token/revoke`)
    if (resp.status !== 200) {
      return false
    }
    return true
  }

  static async generateRecovery(): Promise<RecoveryResponse | boolean> {
    const resp = await apiClientInst.get(`${this.AUTH_BASE}/token/recovery`)
    if (resp.status == 200) {
      let data: RecoveryResponse = resp.data
      return data
    }
    return false
  }

  static async transferUser(data: RecoveryRequest): Promise<boolean> {
    const resp = await apiClientInst.post(`${this.AUTH_BASE}/token/transfer`, data)
    if (resp.status !== 200) {
      return false
    }
    return true
  }
}
