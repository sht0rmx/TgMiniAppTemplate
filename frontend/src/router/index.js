import { createRouter, createWebHistory } from 'vue-router'
import { i18n } from '@/locales/index.js'

import HomeView from '@/views/Home.vue'
import LoginView from '@/views/Login.vue'
import NeedAuthView from '@/views/Errors/NeedAuth.vue'
import SettingsView from '@/views/Settings.vue'
import NotFoundView from '@/views/Errors/NotFound.vue'
import DevicesView from '@/views/Devices.vue'
import UnauthorizedView from '@/views/Errors/Unauthorized.vue'

import { isTgEnv, WebApp } from '@/main.js'


const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { titleKey: 'views.home.header' },
  },
  {
    path: '/need_auth',
    name: 'NeedAuth',
    component: NeedAuthView,
    meta: { titleKey: 'views.need_auth.header' },
  },
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: UnauthorizedView,
    meta: { titleKey: 'views.not_found.code.401.header' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { titleKey: 'views.settings.header' },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { titleKey: 'views.login.header' },
  },
  {
    path: '/settings/devices',
    name: 'Devices',
    component: DevicesView,
    meta: { titleKey: 'views.devices.header' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView,
    meta: { titleKey: 'views.not_found.code.404.header' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.afterEach((to) => {
  const key = to.meta.titleKey
  if (key) {
    document.title = i18n.global.t(key)
  }
  if (["/", "/need_auth"].includes(to.path)) {
    WebApp.BackButton.hide()
  } else {
    WebApp.BackButton.show()
  }
})

router.beforeEach((to, _, next) => {
  if (!isTgEnv && !["/need_auth", "/login"].includes(to.path)) {
    return next('/need_auth')
  }
  next()
})

export default router
