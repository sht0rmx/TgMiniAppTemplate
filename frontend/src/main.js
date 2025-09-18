import 'remixicon/fonts/remixicon.css'
import '@/assets/main.css'

import { createApp } from 'vue'
import { init, backButton, mockTelegramEnv} from '@telegram-apps/sdk-vue';
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


try {
  init();
  console.log('Telegram environment detected')
} catch (err) {
  console.warn('Not inside Telegram, fallback mode')
}


if (backButton.show.isAvailable()) {
  backButton.show();
  backButton.onClick(() => {
    window.history.back();
  });
}

const app = createApp(App)

export let TgApp = app.config.globalProperties.$tg
export let isTgEnv = !!TgApp?.initData

app.use(i18n)
app.use(router)

app.mount('#app')
