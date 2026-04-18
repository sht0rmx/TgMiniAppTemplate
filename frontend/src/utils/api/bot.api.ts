import apiClientInst from './api.ts'

export interface SendMessageResponse {
  detail: string
}

export class BotService {
  private static BASE = '/api/v1/bot'

  static async sendMessage(text: string): Promise<SendMessageResponse | null> {
    try {
      const res = await apiClientInst.post(`${this.BASE}/send`, { text })
      if (res.status === 200) {
        return res.data as SendMessageResponse
      }
      return null
    } catch (e: any) {
      const detail = e?.response?.data?.detail || 'Unknown error'
      return { detail } as SendMessageResponse
    }
  }
}
