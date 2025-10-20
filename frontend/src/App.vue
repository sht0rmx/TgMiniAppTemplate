<script setup>
import { Button } from '@/components/ui/button'
import UpdatePopup from '@/components/UpdatePopup.vue'
import BottomDock from '@/components/BottomDock.vue'
import { isLoading } from '@/main.js'
import SplashScreen from '@/components/SplashScreen.vue'

let hided_dock = ['NeedAuth', 'Login']
</script>

<template>
  <SplashScreen v-if="isLoading" />
  <div v-else class="app-container" :class="['flex flex-col min-h-screen bg-base-200', { 'pb-14': !hided_dock.includes($route.name) }]">
    <main :class="['flex-1 text-sm text-base-content flex justify-center', { 'p-4': !hided_dock.includes($route.name) },]">
      <div :class="['w-full', hided_dock.includes($route.name) ? 'max-w-sm' : 'max-w-2xl']">
        <router-view />
      </div>
    </main>
    <UpdatePopup />
    <BottomDock v-if="!hided_dock.includes($route.name)" />
  </div>
</template>

<style scoped>
.app-container {
  padding-top: calc(var(--tg-safe-area-inset-top, 0px));
  overflow-x: clip;
}
</style>
