import FingerprintJS from '@fingerprintjs/fingerprintjs'

class ApiClient {
  constructor() {
    this.accessToken = null
    this.fpId = null
  }

  async initFingerprint() {
    if (this.fpId) return this.fpId
    const fp = await FingerprintJS.load()
    const res = await fp.get()
    this.fpId = res.visitorId
    localStorage.setItem('fingerprint', this.fpId)
    return this.fpId
  }

  getFingerprint() {
    return this.fpId || localStorage.getItem('fingerprint') || 'default'
  }

  getAccessToken() {
    return this.accessToken
  }

  setTokens({ access_token }) {
    this.accessToken = access_token
  }

  async login(initData) {
    const fp = await this.initFingerprint()
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        initData,
        fingerprint: fp,
        userAgent: navigator.userAgent
      })
    })
    if (!res.ok) throw new Error('login failed')
    const data = await res.json()
    this.setTokens(data)
    return data
  }

  async refreshTokens() {
    const fp = await this.initFingerprint()
    const res = await fetch('/api/v1/tokens/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ fingerprint: fp })
    })
    if (!res.ok) throw new Error('failed to refresh')
    const data = await res.json()
    this.setTokens(data)
    return data.access_token
  }

  async apiFetch(url, opts = {}) {
    opts.headers = opts.headers || {}
    if (this.accessToken) {
      opts.headers['Authorization'] = `Bearer ${this.accessToken}`
    }

    let res = await fetch(url, { ...opts, credentials: 'include' })

    if (res.status === 401) {
      try {
        const newToken = await this.refreshTokens()
        opts.headers['Authorization'] = `Bearer ${newToken}`
        res = await fetch(url, { ...opts, credentials: 'include' })
      } catch {
        throw new Error('unauthorized')
      }
    }

    return res
  }

  async logout() {
    await fetch('/api/v1/tokens/revoke', {
      method: 'POST',
      credentials: 'include'
    })
    this.accessToken = null
    this.fpId = null
    localStorage.removeItem('fingerprint')
  }
}

export const apiClient = new ApiClient()
