<script setup>
import BottomDock from '@/components/BottomDock.vue'
import { retrieveLaunchParams, requestSafeAreaInsets } from '@telegram-apps/sdk';
import { useRoute } from 'vue-router';
import { onMounted } from 'vue';
import { send_auth } from '@/utils/apiclient'

const route = useRoute();

onMounted(async () => {
  if (route.name !== 'NeedAuth') {
    try {
      const { initDataRaw } = retrieveLaunchParams()
      console.log('TG initData:', initDataRaw)
      send_auth(initDataRaw)
    } catch (e) {
      console.warn('TG launch params not available', e)
    }

    if (requestSafeAreaInsets.isAvailable()) {
      const insets = await requestSafeAreaInsets();
      document.documentElement.style.setProperty("--safe-top", insets.top + "px")
      document.documentElement.style.setProperty("--safe-bottom", insets.bottom + "px")
    }
  }
})
</script>


<template>
  <div class= "app-container" :class="['flex flex-col min-h-screen bg-base-200', { 'pb-14': $route.name != 'NeedAuth' }]"> 

    <main :class="['flex-1 text-sm text-base-content flex justify-center', { 'p-4': $route.name != 'NeedAuth' }]">
      <div :class="[
        'w-full',
        $route.name === 'NeedAuth' ? 'max-w-sm' : 'max-w-2xl'
      ]">
        <router-view />
      </div>
    </main>

    <BottomDock v-if="$route.name != 'NeedAuth'" />
  </div>
</template>

<style scoped>
.app-container {
  padding-top: calc(8px + var(--safe-top, 0px));
}
</style>