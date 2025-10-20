import axios from 'axios'
import { useUserStore } from '@/store/user.js'
import { useRouter } from 'vue-router'

const router = useRouter()

const API_URL = import.meta.env.VITE_API_URL

class Client {
  constructor() {
    this.accessToken = null
    this.axios = axios.create({
      baseURL: API_URL,
      withCredentials: true,
      headers: { 'Content-Type': 'application/json' },
    })

    this.axios.interceptors.response.use(
      (res) => res,
      async (err) => {
        const original = err.config

        if (
          err.response?.status === 401 &&
          !original._retry &&
          !original.url.includes('/auth/token/refresh')
        ) {
          original._retry = true
          try {
            const r = await this.refreshTokens()
            if (r.code === 200 && r.access) {
              original.headers['Authorization'] = `Bearer ${r.access}`
              return this.axios(original)
            }
          } catch (e) {
            console.warn('refresh failed', e)
            await router.push('/need_auth')
            return Promise.reject(e)
          }
        }

        if (err.response?.status === 401) {
          console.log('error response', err.response.status, err.response.data)
        }

        return Promise.reject(err)
      },
    )
  }

  getAccessToken() {
    return this.accessToken
  }

  setAccessToken(token) {
    this.accessToken = token
    if (token) {
      this.axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete this.axios.defaults.headers.common['Authorization']
    }
  }

  async login(initData) {
    const res = await this.axios.post('/api/v1/auth/login/webapp', {
      initData,
      userAgent: navigator.userAgent,
    })
    if (res.status === 200) {
      this.setAccessToken(res.data.tokens.access_token)
      return { access: res.data.tokens.access_token, code: res.status }
    }
    return { access: null, code: res.status }
  }

  async refreshTokens() {
    try {
      const res = await this.axios.get('/api/v1/auth/token/refresh')
      if (res.status === 200) {
        this.setAccessToken(res.data.access_token)
        return { access: res.data.access_token, code: res.status }
      }
      return { access: null, code: res.status }
    } catch (err) {
      if (err.response) {
        return { access: null, code: err.response.status }
      }
      return { access: null, code: 500 }
    }
  }

  async logout() {
    await this.axios.get('/api/v1/auth/token/revoke')
    this.setAccessToken(null)
  }

  async check() {
    const store = useUserStore()
    const res = await apiClient.apiFetch('/api/v1/auth/check')

    if (!res || res.status !== 200) {
      store.clearUser()
      await router.push('/need_auth')
    }

    store.setUser(res.data)
  }

  async apiFetch(url, opts = {}) {
    const method = opts.method || 'GET'
    const data = opts.body || opts.data || null
    const headers = opts.headers || {}
    return this.axios({ url, method, data, headers })
  }

  async ping() {
    try {
      const res = await this.apiFetch('/api/v1/ping', { timeout: 3000 })
      return res.status === 200
    } catch (err) {
      console.error('Ping failed:', err)
      throw err
    }
  }
}

export const apiClient = new Client()
