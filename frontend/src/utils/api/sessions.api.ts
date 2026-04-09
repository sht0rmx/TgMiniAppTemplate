import apiClientInst from './api.ts'

export interface SessionInfo {
  dev: string
  system: string
  browser: string
}

export interface Session {
  id: string
  ip: string
  lastUsed: string
  createdAt: string
  info: SessionInfo
  isCurrent: boolean
}

export interface CurrentSessionResponse {
  ip: string
  lastUsed: string
  info: SessionInfo
  session: string
}

export interface AllSessionsResponse {
  sessions: Session[]
  current_session: string
}

export class SessionsService {
  private static SESSIONS_BASE = '/api/v1/session'

  static async getCurrentSession(): Promise<CurrentSessionResponse | null> {
    try {
      const res = await apiClientInst.get(`${this.SESSIONS_BASE}/current`)
      if (res.status === 200) {
        return res.data as CurrentSessionResponse
      }
      return null
    } catch {
      return null
    }
  }

  static async getAllSessions(): Promise<AllSessionsResponse> {
    try {
      const res = await apiClientInst.get(`${this.SESSIONS_BASE}/all`)
      if (res.status === 200) {
        return res.data as AllSessionsResponse
      }
      return { sessions: [], current_session: '' }
    } catch {
      return { sessions: [], current_session: '' }
    }
  }

  static async killSession(sid: string): Promise<boolean> {
    try {
      const res = await apiClientInst.get(`${this.SESSIONS_BASE}/kill/${sid}`)
      return res.status === 200
    } catch {
      return false
    }
  }
}
