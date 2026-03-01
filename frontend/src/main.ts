import '@/assets/main.css'
import 'remixicon/fonts/remixicon.css'
import { computed, createApp, ref, type Ref } from 'vue'
import { createPinia } from 'pinia'

import App from '@/App.vue'
import router from '@/utils/router.ts'
import { i18n } from '@/utils/langs.ts'
import { setTheme } from '@/utils/themes.ts'
import { authInit } from '@/utils/auth.ts'
import { checkTg } from '@/utils/telegram.ts'

if (import.meta.env.DEV) {
  import('eruda').then((eruda) => eruda.default.init())
}

export let isTgEnv: Ref<boolean> = ref(false)
export let isLoading: Ref<boolean> = ref(true)

export let authStatus: Ref<boolean> = ref(false)
export let authRequired: Ref<boolean> = ref(false)
export let lockPage = computed(
  () => authRequired.value && !authStatus.value && router.currentRoute.value.fullPath !== '/login',
)

export let hiddenNav: Ref<boolean> = ref(false)
export let backButton: Ref<boolean> = ref(false)

export let technicalWork: boolean = import.meta.env.VITE_CONSTRUCTION_MODE as boolean
export let unableAccessApi: Ref<boolean> = ref(false)

export const nav_items = [
  { icon: 'ri-home-line', label: 'components.dock.home', to: '/' },
  { icon: 'ri-menu-line', label: 'components.dock.menu', to: '/menu' },
]

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')

setTheme()
checkTg()
authStatus.value = await authInit()

if (!technicalWork && !unableAccessApi.value) {
  isLoading.value = false
}
