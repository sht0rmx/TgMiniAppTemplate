import { isTgEnv } from '@/main.ts'
import router from '@/utils/router.ts'
import type { WebApp as WebAppType } from 'telegram-web-app'

export const WebApp: WebAppType = window.Telegram?.WebApp;

export function getTelegramStartAppAction(): string | null {
  const param = WebApp?.initDataUnsafe?.start_param
  if (!param) return null

  try {
    return atob(param)
  } catch {
    return param
  }
}

export function checkTg() {
  if (window?.Telegram?.WebApp) {
    const data = WebApp.initDataUnsafe
    const valid = data && data.hash && data.user?.id

    if (valid) {
      isTgEnv.value = true
      console.log('Telegram environment detected')

      const isDesktop = WebApp.platform === 'tdesktop'
      if (!isDesktop) {
        WebApp.disableVerticalSwipes()
        WebApp.requestFullscreen()
      }

      WebApp.BackButton.show()
      WebApp.BackButton.onClick(() => router.back())

      WebApp.SettingsButton.show()
      WebApp.SettingsButton.onClick(() => router.push('/menu/settings'))
    } else {
      isTgEnv.value = false
      console.warn('Telegram.WebApp exists, but initData is not valid (opened in browser)')
    }
  } else {
    isTgEnv.value = false
    console.warn('Not inside Telegram, fallback mode')
  }
}