import { createRouter, createWebHistory } from 'vue-router'
import { type RouteRecordRaw } from 'vue-router'

import HomeView from '@/views/Home.vue'
import LoginView from '@/views/Login.vue'

import { isTgEnv, authRequired, authStatus, backButton, hiddenNav } from '@/main.ts'
import ErrorPage from '@/views/NotFound.vue'
import MenuView from '@/views/Menu.vue'
import Settings from '@/views/Settings.vue'
import Devices from '@/views/SettingsViews/Devices.vue'
import ApiKeys from '@/views/SettingsViews/ApiKeys.vue'
import FilesView from '@/views/MenuViews/Files.vue'
import BotChatView from '@/views/MenuViews/BotChat.vue'
import { WebApp } from '@/utils/telegram.ts'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { titleKey: 'views.home.header', auth: false, noTopSafeArea: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { titleKey: 'views.auth.header', auth: false, noNav: true },
  },
  {
    path: '/menu',
    name: 'Menu',
    component: MenuView,
    meta: { titleKey: 'views.menu.header', auth: false },
  },
  {
    path: '/menu/settings',
    name: 'Settings',
    component: Settings,
    meta: { titleKey: 'views.settings.header', auth: false },
  },
  {
    path: '/menu/settings/devices',
    name: 'Devices',
    component: Devices,
    meta: { titleKey: 'views.devices.header', auth: true },
  },
  {
    path: '/menu/settings/apikey',
    name: 'ApiKeys',
    component: ApiKeys,
    meta: { titleKey: 'views.api_keys.header', auth: true },
  },
  {
    path: '/menu/files',
    name: 'Files',
    component: FilesView,
    meta: { titleKey: 'views.files.header', auth: true },
  },
  {
    path: '/menu/bot',
    name: 'BotChat',
    component: BotChatView,
    meta: { titleKey: 'views.bot.header', auth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: ErrorPage,
    meta: { titleKey: 'views.not_found.header', auth: false },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.afterEach((to) => {
  const isDeep = to.path.split('/').length > 2

  if (isDeep) {
    backButton.value = true
    if (isTgEnv.value && WebApp) WebApp.BackButton.show()
  } else {
    backButton.value = false
    if (isTgEnv.value && WebApp) WebApp.BackButton.hide()
  }
})

router.beforeEach((to, _, next) => {
  authRequired.value = to.meta.auth as boolean
  let hideNav: String | any = to.meta.noNav

  if (hideNav) {
    hiddenNav.value = hideNav
  } else {
    hiddenNav.value = false
  }

  if (to.meta.auth && !authStatus.value) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  return next()
})

export default router
