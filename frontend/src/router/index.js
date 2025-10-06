import { createRouter, createWebHistory } from 'vue-router'
import { i18n } from '@/locales/index.js'

import Home from '@/views/Home.vue'
import NeedTgView from '@/views/Errors/NeedTg.vue'
import Settings from '@/views/Settings.vue'
import NotFoundView from '@/views/Errors/NotFound.vue'

import { isTgEnv, WebApp } from '@/main.js'
import Devices from '@/views/Devices.vue'
import NeedAuth from '@/views/Errors/NeedAuth.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { titleKey: 'views.home.header' },
  },
  {
    path: '/need_tg',
    name: 'NeedTg',
    component: NeedTgView,
    meta: { titleKey: 'views.need_auth.header' },
  },
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: NeedAuth,
    meta: { titleKey: 'views.not_found.code.401.header' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { titleKey: 'views.settings.header' },
  },
  {
    path: '/settings/devices',
    name: 'Devices',
    component: Devices,
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
  if (["/", "/need_tg"].includes(to.path)) {
    WebApp.BackButton.hide()
  } else {
    WebApp.BackButton.show()
  }
})

router.beforeEach((to, _, next) => {
  if (!isTgEnv && ["/need_tg"].includes(to.path)) {
    return next('/need_tg')
  }
  next()
})

export default router
