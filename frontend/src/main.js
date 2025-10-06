import 'remixicon/fonts/remixicon.css'
import '@/assets/main.css'

import { createApp } from 'vue'
import { registerSW } from 'virtual:pwa-register'
import { i18n } from '@/locales/index.js'
import { createPinia } from 'pinia'
import { ref } from 'vue'
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
      await router.replace('/need_auth')
      return false
    } else {
      await apiClient.check()
      return true
    }
  } catch (err) {
    console.error('Auth init error:', err)
    await router.replace('/need_auth')
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
  app.mount('#app')
  let ok = await initAuth()
  console.log(ok)
  isLoading.value = false
}


bootstrap()
