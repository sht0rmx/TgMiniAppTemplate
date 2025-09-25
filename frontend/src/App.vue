<script setup>
import BottomDock from '@/components/BottomDock.vue'
import { useRoute } from 'vue-router'
import { onMounted } from 'vue'
import { apiClient } from '@/utils/apiclient'
import { isTgEnv, WebApp } from '@/main.js'

const route = useRoute()

onMounted(async () => {
  if (route.name !== 'NeedAuth') {
    await apiClient.apiFetch('/api/v1/ping')

    if (isTgEnv) {
      const initDataRaw = WebApp.initData

      let token = apiClient.getAccessToken()
      if (!token) {
        try {
          token = await apiClient.refreshTokens()
          console.log('refreshed:', token)
        } catch {
          console.warn('refresh failed, doing login')
        }
      }

      if (!token) {
        await apiClient.login(initDataRaw)
      }
    } else {
      console.warn('TG launch params not available. Not inside a Telegram Web App.')
    }
  }
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
}
</style>
