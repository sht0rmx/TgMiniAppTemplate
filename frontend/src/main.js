import 'remixicon/fonts/remixicon.css'
import '@/assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

export let isTgEnv = !!window.Telegram?.WebApp.initData
export let TgApp

if (isTgEnv) {
  TgApp = window.Telegram.WebApp;
  const BackButton = TgApp.BackButton;

  BackButton.show();
  BackButton.onClick(() => {
    window.history.back();
  });
}

const app = createApp(App)
app.use(router)
app.mount('#app')