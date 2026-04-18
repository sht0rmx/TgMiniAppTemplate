import apiClientInst from './api.ts'

const ACCOUNT_BASE = '/api/v1/account'

export interface LinkTokenResponse {
  token: string
}

async function ok(
  request: () => Promise<{ status: number }>,
  logLabel: string,
): Promise<boolean> {
  try {
    const res = await request()
    return res.status === 200
  } catch (error) {
    console.error(logLabel, error)
    return false
  }
}

export class AccountService {
  static async getTelegramLinkingToken(): Promise<string | null> {
    try {
      const res = await apiClientInst.post(`${ACCOUNT_BASE}/link/telegram/token`, {})
      if (res.status === 200 && res.data.token) {
        return res.data.token
      }
      return null
    } catch (error) {
      console.error('getTelegramLinkingToken', error)
      return null
    }
  }

  static async linkTelegram(initData: string): Promise<boolean> {
    return ok(
      () => apiClientInst.post(`${ACCOUNT_BASE}/link/telegram`, { initData }),
      'linkTelegram',
    )
  }

  static async linkYandex(code: string): Promise<boolean> {
    return ok(
      () => apiClientInst.post(`${ACCOUNT_BASE}/link/yandex`, { code }),
      'linkYandex',
    )
  }

  static async unlinkAccount(provider: 'telegram' | 'yandex'): Promise<boolean> {
    return ok(
      () => apiClientInst.post(`${ACCOUNT_BASE}/unlink/${provider}`, {}),
      `unlinkAccount:${provider}`,
    )
  }

  static async deleteAccount(): Promise<boolean> {
    return ok(() => apiClientInst.delete(`${ACCOUNT_BASE}`), 'deleteAccount')
  }
}
