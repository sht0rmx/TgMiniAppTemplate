<script setup>
import BottomDock from '@/components/BottomDock.vue'
import { useRoute } from 'vue-router';
import { onMounted } from 'vue';
import { send_auth, ping } from '@/utils/apiclient'

const route = useRoute();

onMounted(() => {
  if (route.name !== 'NeedAuth') {
    if (window.Telegram && window.Telegram.WebApp) {
      const WebApp = window.Telegram.WebApp;
      const initDataRaw = WebApp.initData;
      console.log('TG initData:', initDataRaw);
      ping();
      send_auth(initDataRaw);

    } else {
      console.warn('TG launch params not available. Not inside a Telegram Web App.');
    }
  }
});
</script>

<template>
  <div class="app-container"
    :class="['flex flex-col min-h-screen bg-base-200', { 'pb-14': $route.name != 'NeedAuth' }]">

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
  padding-top: calc(8px + var(--tg-safe-area-inset-top, 0px));
}
</style>