<script setup>
import BottomDock from '@/components/BottomDock.vue'
import { apiClient } from '@/api/client.js'
import { isTgEnv, WebApp } from '@/main.js'
import { useRoute, useRouter } from 'vue-router'
import { onBeforeMount } from 'vue'

const route = useRoute()
const router = useRouter()

onBeforeMount(async () => {
  try {
    if (route.name === 'NeedAuth') return

    await apiClient.ping()

    if (!apiClient.getAccessToken()) {
      await apiClient.refreshTokens()
    }

    if (!apiClient.getAccessToken() && isTgEnv) {
      await apiClient.login(WebApp.initData)
    }

    if (!apiClient.getAccessToken()) {
      await router.replace('/need_auth')
    }

    await apiClient.check()
  } catch (err) {
    console.log(err)
    await router.replace('/need_auth')
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
  overflow-x: clip;
}
</style>
