import 'remixicon/fonts/remixicon.css';
import '@/assets/main.css';

import { createApp } from 'vue';
import { registerSW } from 'virtual:pwa-register';
import { i18n } from '@/locales/index.js';

import App from './App.vue';
import router from './router';
import { notifyUpdate } from './components/UpdatePopup.vue';

const updateSW = registerSW({
  onNeedRefresh() {
    notifyUpdate(updateSW);
  },
});

export let isTgEnv = false;

if (window.Telegram && window.Telegram.WebApp) {
  isTgEnv = true;
  console.log('Telegram environment detected');
  const WebApp = window.Telegram.WebApp;

  WebApp.ready();

  WebApp.expand();

  if (WebApp.BackButton.isVisible) {
    WebApp.BackButton.onClick(() => {
      window.history.back();
    });
  }

} else {
  console.warn('Not inside Telegram, fallback mode');
}

const app = createApp(App);

app.use(i18n);
app.use(router);

app.mount('#app');