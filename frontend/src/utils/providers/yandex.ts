const YANDEX_AUTHORIZE = 'https://oauth.yandex.ru/authorize'

export type YandexOAuthState = 'login' | 'link_account'

export function buildYandexOAuthUrl(options: {
  clientId: string
  state: YandexOAuthState
  redirectUri?: string
}): string {
  const { clientId, state, redirectUri } = options
  let url = `${YANDEX_AUTHORIZE}?response_type=code&client_id=${encodeURIComponent(clientId)}&state=${encodeURIComponent(state)}`
  if (redirectUri) {
    url += `&redirect_uri=${encodeURIComponent(redirectUri)}`
  }
  return url
}
