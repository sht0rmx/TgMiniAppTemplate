import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import FingerprintJS from '@fingerprintjs/fingerprintjs'

const fpPromise = FingerprintJS.load()
const API_URL = import.meta.env.VITE_API_URL as string

export interface EmptyResponse {
  detail?: string
}

interface RetryAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

class Client {
  private accessToken: string | null = null
  private axios: AxiosInstance
  private fingerprint: string | null = null

  constructor() {
    this.axios = axios.create({
      baseURL: API_URL,
      withCredentials: true,
      headers: { 'Content-Type': 'application/json' },
      timeout: 5000,
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    this.axios.interceptors.response.use(
      (res: AxiosResponse) => res,
      async (err: AxiosError) => {
        const original = err.config as RetryAxiosRequestConfig

        const isTokensEndpoint = original?.url?.includes('/api/v1/auth/token/get-tokens')
        const isLoginEndpoint = original?.url?.includes('/api/v1/auth/login/webapp')

        if (
          err.response?.status === 401 &&
          original &&
          !original._retry &&
          !isLoginEndpoint &&
          !isTokensEndpoint
        ) {
          original._retry = true

          try {
            await this.refreshTokens()

            const cloned = {
              ...original,
              headers: { ...original.headers },
            }
            delete cloned._retry

            return this.axios(cloned)
          } catch (e) {
            console.warn('refresh failed', e)
            return Promise.reject(e)
          }
        }

        return Promise.reject(err)
      },
    )
  }

  async refreshTokens(): Promise<boolean> {
    const res = await this.axios.get('/api/v1/auth/token/get-tokens')
    if (res.status === 200) {
      this.setAccessToken(res.data.access_token)
      return true
    }
    return false
  }

  getAccessToken(): string | null {
    return this.accessToken
  }

  setAccessToken(token: string | null): void {
    this.accessToken = token
    if (token) {
      this.axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete this.axios.defaults.headers.common['Authorization']
    }
  }

  async setFingerprint(): Promise<string> {
    if (this.fingerprint) return this.fingerprint

    const STORAGE_KEY = 'device_fingerprint'
    const stored = localStorage.getItem(STORAGE_KEY)

    if (stored) {
      this.fingerprint = stored
      this.axios.defaults.headers.common['Fingerprint'] = stored
      return stored
    }

    const fp = await fpPromise
    const result = await fp.get()

    localStorage.setItem(STORAGE_KEY, result.visitorId)
    this.fingerprint = result.visitorId
    this.axios.defaults.headers.common['Fingerprint'] = result.visitorId
    return result.visitorId
  }

  public getAxiosInstance(): AxiosInstance {
    return this.axios
  }
}

export const apiClient = new Client()
await apiClient.setFingerprint()

export const apiClientInst = apiClient.getAxiosInstance()
export default apiClientInst
