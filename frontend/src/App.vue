<script setup lang="ts">
import { computed, watch, ref, onMounted } from 'vue'
import BottomDock from '@/components/BottomDock.vue'
import AuthModal from '@/components/AuthModal.vue'
import RecoveryCodeModal from '@/components/RecoveryCodeModal.vue'
import ConfirmationModal from '@/components/ConfirmationModal.vue'
import SplashScreen from '@/components/SplashScreen.vue'
import {
  hiddenNav,
  isLoading,
  isTgEnv,
  lockPage,
  technicalWork,
  unableAccessApi,
  recoveryCode,
  showRecoveryModal,
  authStatus,
} from '@/main.ts'
import Drawer from '@/components/drawer/Drawer.vue'
import { showPush } from '@/utils/alert'
import Alert from '@/components/alert/Alert.vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getTelegramStartAppAction, WebApp } from '@/utils/providers/telegram'
import { AccountService } from '@/utils/api/account.api'
import { AuthService } from '@/utils/api/auth.api.ts'
import ConfirmLink from './components/ConfirmLink.vue'

const { t, te } = useI18n()
const route = useRoute()
const appName = (import.meta.env.VITE_APP_TITLE as string) || 'App'
const startAppAction = ref<string | null>(null)

const showLinkErrorDialog = ref(false)
const linkErrorMessage = ref('')

const showLinkConfirmDrawer = ref(false)
const pendingLink = ref<{ method: string; payload: any } | null>(null)


const containerClasses = computed(() => [
  'flex flex-col min-h-screen bg-base-300 overflow-hidden',
  { 'blur-sm': lockPage.value },
  { 'pb-15': !hiddenNav.value },
])

const mainClasses = computed(() => [
  'flex-1 flex overflow-y-auto',
  isTgEnv.value ? 'px-4' : 'px-4 md:px-6 pt-4',
])

if (technicalWork) {
  showPush('splash.construction', '', 'alert-info', 'ri-server-line', false)
}

const confirmTitle = computed(() => {
  if (!pendingLink.value) { return t('views.auth.link_confirm_title') }

  switch (pendingLink.value.method) {
    case 'telegram':
      return t('views.auth.ya.link_confirm_title')
    case 'yandex':
      return t('views.auth.yandex.link_confirm_title')
    default:
      return t('views.auth.link_confirm_title')
  }
})

const confirmHint = computed(() => {
  if (!pendingLink.value) { return t('views.auth.link_confirm_hint') }

  switch (pendingLink.value.method) {
    case 'telegram':
      return t('views.auth.ya.link_confirm_hint')
    case 'yandex':
      return t('views.auth.yandex.link_confirm_hint')
    default:
      return t('views.auth.link_confirm_hint')
  }
})

const tryLinkFromStartApp = async (method: string, payload: any) => {
  if (!authStatus.value) return
  pendingLink.value = { method, payload }
  showLinkConfirmDrawer.value = true
}

const tryLinkTelegramFromStartApp = async () => {
  if (!WebApp || !authStatus.value) return
  try {
    const initData = WebApp.initData || ''
    if (!initData) return
    await tryLinkFromStartApp('telegram', initData)
  } catch (error) {
    console.error('Telegram startapp linking error:', error)
    linkErrorMessage.value = 'views.auth.ya.error'
    showLinkErrorDialog.value = true
  }
}

const handleLinkAccept = async () => {
  if (!pendingLink.value) return
  try {
    let linked = false
    if (pendingLink.value.method === 'telegram') {
      linked = await AccountService.linkTelegram(pendingLink.value.payload)
    } else if (pendingLink.value.method === 'yandex') {
      linked = await AccountService.linkYandex(pendingLink.value.payload)
    }
    if (linked) {
      await AuthService.check()
      showPush('views.auth.link_success', '', 'alert-success', 'ri-check-line')
      showLinkConfirmDrawer.value = false
      pendingLink.value = null
    } else {
      linkErrorMessage.value = 'views.auth.link_error'
      showLinkErrorDialog.value = true
    }
  } catch (error) {
    console.error('Account linking error:', error)
    linkErrorMessage.value = 'views.auth.link_error'
    showLinkErrorDialog.value = true
  } finally {
    showLinkConfirmDrawer.value = false
    pendingLink.value = null
  }
}

const handleLinkDecline = () => {
  showLinkConfirmDrawer.value = false
  pendingLink.value = null
}

onMounted(() => {
  if (!WebApp) { return }

  const action = getTelegramStartAppAction()
  if (!action) { return }

  startAppAction.value = action
  if (action.startsWith('link_telegram') && authStatus.value) {
    tryLinkTelegramFromStartApp()
  }
})

watch(() => authStatus.value, async (value) => {
  if (value && startAppAction.value?.startsWith('link_telegram')) {
    await tryLinkTelegramFromStartApp()
  }
})

watch(() => route.meta.titleKey, (key) => {
  if (typeof key === 'string' && te(key)) {
    document.title = String(t(key))
  } else {
    document.title = appName
  }
}, { immediate: true })

watch(unableAccessApi, () => {
  if (!technicalWork && unableAccessApi.value) {
    showPush('splash.api_unavailable', '', 'alert-warning', 'ri-error-warning-line', false)
  }
})

</script>

<template>
  <Drawer>
    <SplashScreen v-show="isLoading" />

    <div v-show="!isLoading" :class="containerClasses" class="app-container md:pb-0 min-h-screen">
      <main :class="mainClasses">
        <div class="w-full">
          <router-view />
        </div>
      </main>

      <BottomDock v-if="!hiddenNav && !isLoading" />
    </div>

    <AuthModal v-if="!isLoading" />
    <RecoveryCodeModal :code="recoveryCode" :is-open="showRecoveryModal" @close="showRecoveryModal = false" />
    <ConfirmationModal :is-open="showLinkErrorDialog" title="views.auth.ya.error" :message="linkErrorMessage"
      confirm-text="common.close" confirm-button-class="btn-primary" @confirm="showLinkErrorDialog = false"
      @cancel="showLinkErrorDialog = false" />

    <ConfirmLink :confirmTitle="confirmTitle" :confirmHint="confirmHint" :showLinkConfirmDrawer="showLinkConfirmDrawer"
      :handleLinkAccept="handleLinkAccept" :handleLinkDecline="handleLinkDecline" />
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
