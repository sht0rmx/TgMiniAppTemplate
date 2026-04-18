import { useUserStore } from '@/utils/stores/user.ts'
import apiClientInst, { apiClient } from './api.ts'
import router from '@/utils/router.ts'
import { authStatus } from '@/main.ts'

const API_URL = import.meta.env.VITE_API_URL as string
const FRONT_URL = import.meta.env.VITE_FRONTEND_URL as string

const AUTH_BASE = '/api/v1/auth'

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
  private static async postAccess(
    path: string,
    body: unknown,
  ): Promise<AccessResponse | null> {
    try {
      const res = await apiClientInst.post(`${AUTH_BASE}${path}`, body)
      if (res.status === 200 && res.data?.access_token) {
        apiClient.setAccessToken(res.data.access_token)
        return res.data as AccessResponse
      }
      return null
    } catch (e) {
      console.error('AuthService.postAccess', path, e)
      return null
    }
  }

  static async webappLogin(data: WebAppLoginRequest): Promise<AccessResponse | null> {
    return this.postAccess('/login/webapp', data)
  }

  static async yandexLogin(data: YandexLoginRequest): Promise<AccessResponse | null> {
    return this.postAccess('/login/yandex', data)
  }

  static async transferAccount(data: RecoveryRequest): Promise<boolean> {
    try {
      const res = await apiClientInst.post(`${AUTH_BASE}/token/transfer`, data)
      return res.status === 200
    } catch (e) {
      console.error('AuthService.transferAccount', e)
      return false
    }
  }

  static async startQrLogin() {
    const res = await apiClientInst.get(`${AUTH_BASE}/login/getqr`)

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
    let evtSource: EventSource | null = null

    const cancel = () => {
      if (evtSource) {
        evtSource.close()
        evtSource = null
      }
    }

    const connect = (id: string) => {
      return new Promise<string>((resolve, reject) => {
        const url = `${API_URL}api/v1/auth/sse/check/${id}`

        try {
          evtSource = new EventSource(url)
        } catch (error) {
          reject(new Error('EventSource initialization failed.'))
          return
        }

        evtSource.onmessage = (event: MessageEvent) => {
          const data = JSON.parse(event.data)
          if (data.type === 'auth_success' && data.access_token) {
            cancel()
            apiClient.setAccessToken(data.access_token)
            resolve(data.access_token as string)
          } else if (data.type === 'auth_denied' || data.type === 'timeout') {
            cancel()
            reject(new Error(data.message || 'Login denied or timed out.'))
          }
        }

        evtSource.onerror = () => {
          cancel()
          setTimeout(() => {
            connect(id).then(resolve).catch(reject)
          }, 1000)
        }
      })
    }

    return { authPromise: connect(loginId), cancel }
  }

  /** Подтвердить вход с другого устройства по login_id из QR (GET …/login/accept/:id) */
  static async acceptRemoteLogin(loginId: string): Promise<boolean> {
    try {
      const resp = await apiClientInst.get(`${AUTH_BASE}/login/accept/${loginId}`)
      return resp.status === 200
    } catch {
      return false
    }
  }

  static async acceptByCode(code: string): Promise<boolean> {
    try {
      const resp = await apiClientInst.get(`${AUTH_BASE}/login/code/accept/${code}`)
      return resp.status === 200
    } catch {
      return false
    }
  }

  static async check(): Promise<boolean> {
    const store = useUserStore()
    const res = await apiClientInst.get(`${AUTH_BASE}/check`)

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
      const resp = await apiClientInst.get(`${AUTH_BASE}/token/recreate-tokens`)
      if (resp.status === 200 && resp.data?.access_token) {
        apiClient.setAccessToken(resp.data.access_token)
        return true
      }
      return false
    } catch {
      return false
    }
  }

  static async revokeRefreshSession(): Promise<boolean> {
    try {
      const resp = await apiClientInst.get(`${AUTH_BASE}/token/revoke`)
      return resp.status === 200
    } catch {
      return false
    }
  }

  static async generateRecovery(): Promise<RecoveryResponse | false> {
    try {
      const resp = await apiClientInst.get(`${AUTH_BASE}/token/recovery`)
      if (resp.status === 200) {
        return resp.data as RecoveryResponse
      }
      return false
    } catch {
      return false
    }
  }
}
