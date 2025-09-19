import 'remixicon/fonts/remixicon.css'
import '@/assets/main.css'

import { createApp } from 'vue'
import { init, backButton, requestFullscreen, viewport} from '@telegram-apps/sdk-vue';
import { registerSW } from 'virtual:pwa-register'
import { i18n } from '@/locales/index.js'

import App from './App.vue'
import router from './router'
import { notifyUpdate } from './components/UpdatePopup.vue'


const updateSW = registerSW({
  onNeedRefresh() {
    notifyUpdate(updateSW)
  },
})

let initdata_avalible = false

try {
  await init();
  initdata_avalible = true
  console.log('Telegram environment detected')
} catch (err) {
  console.warn('Not inside Telegram, fallback mode')
}

export let isTgEnv = initdata_avalible

 if (isTgEnv) {
    await viewport.mount()
    await requestFullscreen()

    if (backButton.show.isAvailable()) {
      await backButton.mount()
      await backButton.show()
      backButton.onClick(() => {
        window.history.back()
      })
    }
  }

const app = createApp(App)

app.use(i18n)
app.use(router)

app.mount('#app')
