import apiClientInst from './api.ts'

export interface ApiKey {
  id: string
  name: string
  banned: boolean
  createdAt: string
}

export interface AllApiKeysResponse {
  keys: ApiKey[]
}

export interface CreateApiKeyResponse {
  detail: string
  key: string
  name: string
}

export class ApiKeysService {
  private static BASE = '/api/v1/apikeys'

  /** GET /api/v1/apikeys/all */
  static async getAll(): Promise<ApiKey[]> {
    try {
      const res = await apiClientInst.get(`${this.BASE}/all`)
      if (res.status === 200) {
        return (res.data as AllApiKeysResponse).keys
      }
      return []
    } catch {
      return []
    }
  }

  /** POST /api/v1/apikeys/create */
  static async create(name: string): Promise<CreateApiKeyResponse | null> {
    try {
      const res = await apiClientInst.post(`${this.BASE}/create`, { name })
      if (res.status === 201) {
        return res.data as CreateApiKeyResponse
      }
      return null
    } catch {
      return null
    }
  }

  /** DELETE /api/v1/apikeys/:id */
  static async remove(keyId: string): Promise<boolean> {
    try {
      const res = await apiClientInst.delete(`${this.BASE}/${keyId}`)
      return res.status === 200
    } catch {
      return false
    }
  }

  /** PATCH /api/v1/apikeys/:id/ban */
  static async toggleBan(keyId: string): Promise<boolean | null> {
    try {
      const res = await apiClientInst.patch(`${this.BASE}/${keyId}/ban`)
      if (res.status === 200) {
        return res.data.banned as boolean
      }
      return null
    } catch {
      return null
    }
  }
}
