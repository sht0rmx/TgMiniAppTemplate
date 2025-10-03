<script setup>
import BottomDock from '@/components/BottomDock.vue'
import { useRoute, useRouter } from 'vue-router'
import { onMounted, ref } from 'vue'
import { apiClient } from '@/api/client.js'
import { isTgEnv, WebApp } from '@/main.js'
import { useUserStore } from '@/store/user.js'

const route = useRoute()
const router = useRouter()
const initialized = ref(false)

onMounted(async () => {
  if (route.name === 'NeedAuth') return

  let api_status = await apiClient.ping()
  console.log('ping api:', api_status)

  let token = apiClient.getAccessToken()
  console.log('access token:', token)

  if (!token) {
    console.log('token not found, refreshing')
    const r = await apiClient.refreshTokens()
    console.log('refresh response', r)
    if (r.code === 200) {
      token = r.access
      console.log('> refresh successful, token: ', token)
    } else {
      console.log('> cant refresh! status: ', r.status)
    }
  }

  if (!token && isTgEnv) {
    console.log('token not found, login')
    const r = await apiClient.login(WebApp.initData)
    console.log('login response', r)
    if (r.code === 200) {
      token = r.access
      console.log('> login successful, token: ', token)
    }
  }

  if (!token) {
    console.log('cant get token!')
    return await router.push('/need_auth')
  }

  const store = useUserStore()
  console.log('validate token: ', token)

  const res = await apiClient.apiFetch('/api/v1/auth/check')
  console.log('response', res)

  if (!res || res.status !== 200) {
    store.clearUser()
    console.log('invalid token!')
    return await router.push('/need_auth')
  }

  store.setUser(res.data)

  initialized.value = true
  WebApp.ready()
})

</script>

<template>
  <div
    class="app-container"
    :class="['flex flex-col min-h-screen bg-base-200', { 'pb-14': $route.name !== 'NeedAuth' }]"
  >
    <main
      :class="[
        'flex-1 text-sm text-base-content flex justify-center',
        { 'p-4': $route.name !== 'NeedAuth' },
      ]"
    >
      <div :class="['w-full', $route.name === 'NeedAuth' ? 'max-w-sm' : 'max-w-2xl']">
        <router-view />
      </div>
    </main>

    <BottomDock v-if="$route.name !== 'NeedAuth'" />
  </div>
</template>

<style scoped>
.app-container {
  padding-top: calc(var(--tg-safe-area-inset-top, 0px));
  overflow-x: clip;
}
</style>
