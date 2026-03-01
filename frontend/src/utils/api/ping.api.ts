import apiClientInst from './api.ts'

export class PingService {
  private static AUTH_BASE = '/api/v1'
  /** GET /api/v1/ping - Check health of api */
  static async pingPong(): Promise<boolean> {
    try {
      const resp = await apiClientInst.get(`${this.AUTH_BASE}/ping`)
      if (resp.status !== 200) {
        return false
      }
      return true
    } catch (e) {
      return false
    }
  }
}
