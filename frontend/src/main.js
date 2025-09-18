import 'remixicon/fonts/remixicon.css'
import '@/assets/main.css'

import { createApp } from 'vue'
import { init } from '@telegram-apps/sdk-vue';
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

init()

backButton.mount();

const off = backButton.onClick(() => {
  window.history.back();
});

const app = createApp(App)

app.use(i18n)
app.use(router)

app.mount('#app')

export let TgApp = app.config.globalProperties.$tg
export let isTgEnv = !!TgApp?.initData
