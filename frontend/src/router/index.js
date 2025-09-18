import { createRouter, createWebHistory } from 'vue-router'
import { i18n } from '@/locales/index.js'

import Home from '@/views/Home.vue'
import NeedAuthView from '@/views/NeedAuth.vue'
import SettingsView from '@/views/Settings.vue'
import NotFoundView from '@/views/NotFound.vue'

import { isTgEnv } from '@/main.js'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { titleKey: 'views.home.header' },
  },
  {
    path: '/need_auth',
    name: 'NeedAuth',
    component: NeedAuthView,
    meta: { titleKey: 'views.need_auth.header' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { titleKey: 'views.settings.header' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView,
    meta: { titleKey: 'views.not_found.header' },
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
})

router.beforeEach((to, _, next) => {
  if (!isTgEnv && to.path !== '/need_auth') {
    return next('/need_auth')
  }
  next()
})

export default router
