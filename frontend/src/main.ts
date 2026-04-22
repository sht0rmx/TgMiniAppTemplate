import '@/assets/main.css'
import 'remixicon/fonts/remixicon.css'
import { computed, createApp, ref, type Ref } from 'vue'
import { createPinia } from 'pinia'

import App from '@/App.vue'
import router from '@/utils/router.ts'
import { i18n, initializeLocale, fetchAvailableLocales } from '@/utils/managers/langs'
import { setTheme } from '@/utils/managers/themes'
import { authInit } from '@/utils/auth.ts'
import { checkTg } from '@/utils/providers/telegram'
import { handleError } from '@/utils/help.ts'

if (import.meta.env.DEV) {
  import('eruda').then((eruda) => eruda.default.init())
}

export let isTgEnv: Ref<boolean> = ref(false)
export let isLoading: Ref<boolean> = ref(true)

export let hiddenNav: Ref<boolean> = ref(false)
export let backButton: Ref<boolean> = ref(false)

export let authStatus: Ref<boolean> = ref(false)
export let authRequired: Ref<boolean> = ref(false)
export let lockPage = computed(
  () => authRequired.value && !authStatus.value && router.currentRoute.value.fullPath !== '/login',
)
export let recoveryCode: Ref<string> = ref('')
export let showRecoveryModal: Ref<boolean> = ref(false)

export const drawerOpen = ref(false)

export const showRecoveryCodeModal = (code: string) => {
  recoveryCode.value = code
  showRecoveryModal.value = true
}

export let technicalWork: boolean = import.meta.env.VITE_CONSTRUCTION_MODE as boolean
export let unableAccessApi: Ref<boolean> = ref(false)

export const nav_items = [
  { icon: 'ri-home-line', label: 'components.dock.home', to: '/' },
  { icon: 'ri-menu-line', label: 'components.dock.menu', to: '/menu' },
]

const initApp = async () => {
  await initializeLocale()
  await fetchAvailableLocales()
  checkTg()
  authStatus.value = await authInit()
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.config.errorHandler = (err, _, info) => {
  console.error('[Vue Error]', err, info)
  handleError(err, 'Vue Error')
}

window.addEventListener('unhandledrejection', (event) => {
  console.error('[Unhandled Promise Rejection]', event.reason)
  handleError(event.reason, 'Unhandled Promise Rejection')
})

window.addEventListener('error', (event) => {
  console.error('[Global Error]', event.error)
  handleError(event.error, 'Global Error')
})

setTheme()
app.mount('#app')
await initApp().then(() => {
  if (!technicalWork && !unableAccessApi.value) {
    isLoading.value = false
  }
})

