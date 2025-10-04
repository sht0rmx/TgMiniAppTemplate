import 'remixicon/fonts/remixicon.css'
import '@/assets/main.css'

import { createApp } from 'vue'
// import { registerSW } from 'virtual:pwa-register'
import { i18n } from '@/locales/index.js'
import { createPinia } from 'pinia'
import piniaPersistedstate from 'pinia-plugin-persistedstate'

import App from './App.vue'
import router from './router'
// import { notifyUpdate } from './components/UpdatePopup.vue'

// const updateSW = registerSW({
//   onNeedRefresh() {
//     notifyUpdate(updateSW)
//   },
// })

export let isTgEnv = false
export let WebApp = null

if (window?.Telegram?.WebApp) {
  WebApp = window.Telegram.WebApp
  const initDataRaw = WebApp.initData || ""

  if (initDataRaw.length > 0) {
    isTgEnv = true
    console.log('Telegram environment detected')

    const isDesktop = WebApp.platform === "tdesktop"
    const openedFromInlineButton = !!WebApp.initDataUnsafe?.start_param

    console.log(isDesktop, openedFromInlineButton)

    if (!isDesktop) {
      WebApp.disableVerticalSwipes()
      WebApp.requestFullscreen()
    }

    WebApp.BackButton.show()
    WebApp.BackButton.onClick(() => {
      window.history.back()
    })
    WebApp.ready()
  } else {
    console.warn('Telegram.WebApp found, but no initData (probably opened in browser)')
  }
} else {
  console.warn('Not inside Telegram, fallback mode')
}

const pinia = createPinia()
pinia.use(piniaPersistedstate)

const app = createApp(App)

app.use(pinia)
app.use(i18n)
app.use(router)

app.mount('#app')
