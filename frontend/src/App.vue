<script setup lang="ts">
import { computed, watch } from 'vue'
import BottomDock from '@/components/BottomDock.vue'
import AuthModal from '@/components/AuthModal.vue'
import SplashScreen from '@/components/SplashScreen.vue'
import { hiddenNav, isLoading, isTgEnv, lockPage, technicalWork, unableAccessApi } from '@/main.ts'
import Drawer from '@/components/drawer/Drawer.vue'
import { showPush } from '@/components/alert/index.ts'
import Alert from '@/components/alert/Alert.vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t, te } = useI18n()
const route = useRoute()

const containerClasses = computed(() => [
  'flex flex-col min-h-screen bg-base-300 overflow-hidden',
  { 'blur-sm': lockPage.value },
  { 'pb-20': !hiddenNav.value },
])

const mainClasses = computed(() => [
  'flex-1 flex overflow-y-auto',
  isTgEnv.value ? 'px-4' : 'px-4 md:px-6 pt-4',

])

watch(unableAccessApi, () => {
  if (!technicalWork && unableAccessApi.value) {
    showPush('splash.api_unavalible', '', 'alert-warning', 'ri-error-warning-line', false)
  }
})

if (technicalWork) {
  showPush('splash.construction', '', 'alert-info', 'ri-server-line', false)
}
const appName = import.meta.env.VITE_APP_TITLE as string || 'App'

watch(
  () => route.meta.titleKey,
  (key) => {
    if (typeof key === 'string' && te(key)) {
      document.title = String(t(key))
    } else {
      document.title = appName
    }
  },
  { immediate: true }
)
</script>

<template>
  <Drawer>
    <SplashScreen v-show="isLoading" />

    <div v-show="!isLoading" :class="containerClasses" class="app-container lg:pb-4 min-h-screen">
      <main :class="mainClasses">
        <div class="w-full">
          <router-view />
        </div>
      </main>

      <BottomDock v-if="!hiddenNav && !isLoading" />
    </div>

    <AuthModal />
    <Alert />
  </Drawer>
</template>

<style>
html,
body {
  height: 100%;
  margin: 0;
  overflow: hidden;
  overscroll-behavior: none;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding-top: calc(var(--tg-safe-area-inset-top, 0px));
  overflow: hidden;
}

main {
  overscroll-behavior-y: contain;
  -webkit-overflow-scrolling: touch;
}
</style>
