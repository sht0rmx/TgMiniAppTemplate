import 'remixicon/fonts/remixicon.css'
import '@/assets/main.css'

import { createApp, ref } from 'vue'
import { registerSW } from 'virtual:pwa-register'
import { i18n } from '@/locales/index.js'
import { createPinia } from 'pinia'
import piniaPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import { apiClient } from '@/api/client.js'
import { notifyUpdate } from './components/UpdatePopup.vue'

const updateSW = registerSW({
  onNeedRefresh() {
    notifyUpdate(updateSW)
  },
})

export let isTgEnv = false
export let WebApp = null
export let isLoading = ref(true)

const sysDark = window.matchMedia('(prefers-color-scheme: dark)')

function setTheme(isDark) {
  if (isDark) {
    document.documentElement.classList.add('dark')
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    document.documentElement.setAttribute('data-theme', 'light')
  }
}

sysDark.addEventListener('change', e => setTheme(e.matches))

async function initAuth() {
  try {
    await apiClient.ping()

    if (!apiClient.getAccessToken()) {
      await apiClient.refreshTokens()
    }

    if (!apiClient.getAccessToken() && isTgEnv) {
      await apiClient.login(WebApp.initData)
    }

    if (!apiClient.getAccessToken()) {
      return false
    } else {
      await apiClient.check()
      return true
    }
  } catch (err) {
    console.error('Auth init error:', err)
    return false
  }
}

if (window?.Telegram?.WebApp) {
  WebApp = window.Telegram.WebApp
  const initDataRaw = WebApp.initData || ''

  if (initDataRaw.length > 0) {
    isTgEnv = true
    console.log('Telegram environment detected')

    const isDesktop = WebApp.platform === 'tdesktop'
    if (!isDesktop) {
      WebApp.disableVerticalSwipes()
      WebApp.requestFullscreen()
    }

    WebApp.BackButton.show()
    WebApp.BackButton.onClick(() => router.back())
  } else {
    console.warn('Telegram.WebApp found, but no initData (probably opened in browser)')
  }
} else {
  console.warn('Not inside Telegram, fallback mode')
}

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()
  pinia.use(piniaPersistedstate)
  app.use(pinia)
  app.use(i18n)
  app.use(router)

  setTheme(sysDark.matches)

  app.mount('#app')

  const ok = await initAuth()
  const current = router.currentRoute.value.name

  if (!ok && !isTgEnv && !['need_auth', 'unauthorized'].includes(current)) {
    await router.push('/need_auth')
  }
  if (!ok && isTgEnv && !['need_auth', 'unauthorized'].includes(current)) {
    await router.push('/unauthorized')
  }

  console.log('Auth OK:', ok)
  isLoading.value = false
}

bootstrap()
