import { createRouter, createWebHistory } from 'vue-router'

import AppView from '@/views/Home.vue'
import NeedAuthView from '@/views/NeedAuth.vue'
import SettingsView from '@/views/Settings.vue'
import NotFoundView from '@/views/NotFound.vue'

import { isTgEnv } from '@/main.js'

const routes = [
  { path: '/', component: AppView },
  { path: '/need_auth', component: NeedAuthView },
  { path: '/settings', component: SettingsView },
  { path: '/:pathMatch(.*)*', component: NotFoundView },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  if (!isTgEnv && to.path !== '/need_auth') {
    return next('/need_auth')
  }
  next()
})

export default router
