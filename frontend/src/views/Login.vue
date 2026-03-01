<script setup lang="ts">
import { apiClient } from '@/utils/api/api'
import { AuthService } from '@/utils/api/auth.api'
import { showPush } from '@/components/alert'
import QrCode from '@/components/QrCode.vue'
import { isLoading, isTgEnv } from '@/main'
import { onMounted, ref, type Ref, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { WebApp } from '@/utils/telegram.ts'

const route = useRoute()
const router = useRouter()

const qrUrl: Ref<string> = ref('')
const loginCode: Ref<string> = ref('')
const qrStarted: Ref<boolean> = ref(false)
const enableSpinner: Ref<boolean> = ref(false)
const spinnerStatus: Ref<string> = ref('')
let authPromise: Promise<unknown> | null = null
let sseCancel: (() => void) | null = null
let loginId: string = ''

let redirect_to: string = '/'

let timer: number | null = null
const QR_LIFETIME = 5 * 60 * 1000

const openLink = (url: string): void => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

function stopQR() {
  qrUrl.value = ''
  loginCode.value = ''
  if (sseCancel) sseCancel()
  sseCancel = null

  if (timer) clearTimeout(timer)
  timer = null
}

async function LoginTg() {
  enableSpinner.value = true
  spinnerStatus.value = 'views.auth.initdata'
  let res = false

  if (WebApp && isTgEnv.value) {
    res = await AuthService.webappLogin({ initData: WebApp.initData })
    enableSpinner.value = false
  }

  if (res) {
    return true
  }
  return false
}

async function startQR(): Promise<any> {
  stopQR()
  enableSpinner.value = true
  spinnerStatus.value = 'views.auth.qr_gen'
  let resp = null

  resp = await AuthService.startQrLogin()
  enableSpinner.value = false

  loginId = resp.loginId
  loginCode.value = resp.loginCode
  qrUrl.value = resp.qrUrl
  qrStarted.value = true
  authPromise = resp.authPromise
  sseCancel = resp.cancelSse

  timer = window.setTimeout(() => {
    stopQR()
  }, QR_LIFETIME)

  authPromise
    ?.then(async (token) => {
      stopQR()

      try {
        await AuthService.recreateTokens()
      } catch (e) {
        console.warn('Failed to establish refresh session:', e)
      }
      await AuthService.check()

      showPush('views.auth.login_success', '', 'alert-success', 'ri-check-line')
      router.push(redirect_to)
    })
    .catch((err) => {
      console.warn('Auth rejected:', err)
      stopQR()
      showPush('views.auth.login_rejected', '', 'alert-warning', 'ri-error-warning-line')
    })
}

async function successPush() {
  isLoading.value = false
  let state = AuthService.check()
  if (!state) {
    showPush('views.auth.login_error', '', 'alert-danger', 'ri-close-line')
    return null
  }
  showPush('views.auth.login_success', '', 'alert-success', 'ri-check-line')
  router.push(redirect_to)
  return null
}

async function startLogin() {
  try {
    redirect_to = String(route.query.redirect)
  } catch (e) {
    redirect_to = '/'
  }

  if (redirect_to === '' || redirect_to === '/login') {
    redirect_to = '/'
  }

  let res = false
  isLoading.value = true

  try {
    res = await apiClient.refreshTokens()
  } catch {
    null
  }

  if (res) {
    await successPush()
  } else if (isTgEnv.value) {
    if (await LoginTg()) {
      await successPush()
    } else {
      showPush('views.auth.miniapp_error', '', 'alert-warning', 'ri-error-warning-line')
    }
  } else {
    await startQR()
    window.setTimeout(() => {
      isLoading.value = false
    }, 200)
  }
}

onMounted(() => startLogin())
onBeforeUnmount(() => stopQR())
</script>

<template>
  <div class="flex flex-col min-h-full items-center justify-center px-4">
    <div class="card bg-base-100 lg:w-90">
      <div class="card-body flex flex-col items-center text-center gap-3">
        <div class="flex flex-col items-center justify-center">
          <i class="ri-user-line text-3xl" />
          <h2 class="card-title text-2xl">{{ $t('views.auth.title') }}</h2>
          <p class="opacity-70">{{ $t('views.auth.hint') }}</p>
        </div>
        <div v-if="!qrUrl" class="card w-50 h-50 bg-base-200/30">
          <div class="card-body flex flex-col items-center justify-center h-full text-center">
            <button
              v-if="qrStarted"
              class="btn btn-small btn-accent btn-soft flex flex-row items-center gap-1"
              @click="startLogin()"
            >
              <i class="ri-reset-right-line text-base"></i>
              <span class="text-base">{{ $t('views.auth.try_again') }}</span>
            </button>
            <div v-else-if="enableSpinner" class="flex flex-col justify-center items-center">
              <span class="loading loading-spinner loading-xl text-primary"></span>
              <span class="opacity-70">{{ $t(spinnerStatus) }}</span>
            </div>
          </div>
        </div>
        <QrCode v-else :url="qrUrl"></QrCode>

        <div v-if="loginCode" class="flex flex-col items-center gap-1">
          <p class="text-xs opacity-50">{{ $t('views.auth.code_hint') }}</p>
          <code
            class="text-lg font-mono font-bold tracking-widest select-all bg-base-200 px-4 py-1.5 rounded-lg lowercase"
            >{{ loginCode.toLowerCase() }}</code
          >
        </div>

        <div class="flex flex-row gap-3">
          <button
            class="btn btn-sm btn-square"
            @click="openLink('https://github.com/sht0rmx/tgminiapptemplate')"
          >
            <i class="ri-github-line text-xl" />
          </button>

          <button class="btn btn-sm btn-square" @click="openLink('https://t.me/sniplabot')">
            <i class="ri-telegram-2-line text-xl" />
          </button>
        </div>
      </div>
    </div>
    <footer class="footer sm:footer-horizontal footer-center bg-base-300 text-base-content p-4">
      <button class="btn btn-ghost btn-sm" @click="$router.push('/')">
        <span class="uppercase tracking-widest">{{ $t('views.auth.skip_login') }}</span>
      </button>
    </footer>
  </div>
</template>
