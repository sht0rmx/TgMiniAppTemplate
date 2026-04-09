<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AuthService } from '@/utils/api/auth.api'
import { AccountService } from '@/utils/api/account.api'
import { showPush } from '@/components/alert'
import { authStatus, showRecoveryCodeModal } from '@/main'

const route = useRoute()
const router = useRouter()

const isProcessing = ref(true)
const errorMessage = ref('')
const isLinking = ref(false)

onMounted(async () => {
  try {
    const code = route.query.code as string
    const state = route.query.state as string

    if (!code) {
      errorMessage.value = 'Missing authorization code'
      isProcessing.value = false
      showPush('views.auth.error', 'Missing authorization code', 'alert-warning', 'ri-close-line')
      setTimeout(() => router.push('/login'), 3000)
      return
    }

    isLinking.value = state === 'link_account'

    if (isLinking.value) {
      const result = await AccountService.linkYandex(code)

      if (result) {
        showPush('views.auth.ya.link_success', '', 'alert-success', 'ri-check-line')
        await AuthService.check()
        setTimeout(() => {
          isProcessing.value = false
          router.push('/menu/settings')
        }, 1500)
      } else {
        throw new Error('Account linking failed')
      }
    } else {
      const result = await AuthService.yandexLogin({ code })

      if (result) {
        if (result.recovery_code) {
          // Show recovery code modal
          showRecoveryCodeModal(result.recovery_code)
        }
        showPush('views.auth.ya.login_success', '', 'alert-success', 'ri-check-line')
        setTimeout(async () => {
          let r = await AuthService.check()
          authStatus.value = true
          isProcessing.value = false
          await router.push('/')
        }, 1500)
      } else {
        throw new Error('Login failed')
      }
    }
  } catch (error) {
    console.error('Yandex OAuth error:', error)
    errorMessage.value = 'Authentication failed'
    showPush('views.auth.ya.error', '', 'alert-warning', 'ri-close-line')
    isProcessing.value = false
    setTimeout(() => router.push(isLinking.value ? '/menu/settings' : '/login'), 3000)
  }
})
</script>

<template>
  <div class="flex w-full h-full items-center justify-center flex-col text-center">
    <div v-if="isProcessing">
      <span class="loading loading-spinner text-info w-15 h-15 my-2"></span>

      <h2 class="text-2xl font-bold">{{ $t('views.auth.ya.processing') }}</h2>
      <p class="text-base opacity-60">{{ $t('views.auth.ya.auto_redirect') }}</p>
      <div class="mt-4 text-sm opacity-30">
        {{ $t('views.auth.ya.redirecting_shortly') }}
      </div>
    </div>

    <div v-else-if="errorMessage">
      <div class="mb-6">
        <i class="text-7xl ri-close-large-line text-error"></i>
      </div>
      <h2 class="text-2xl font-bold text-error">{{ $t('views.auth.ya.error') }}</h2>
      <p class="opacity-60 mb-6">{{ errorMessage }}</p>
      <p class="mt-4 text-sm opacity-30">{{ $t('views.auth.ya.redirecting_login') }}</p>
    </div>

    <div v-else>
      <div class="mb-6">
        <i class="text-7xl ri-checkbox-circle-line text-success"></i>
      </div>
      <h2 class="text-2xl font-bold text-success">{{ $t('views.auth.ya.login_success') }}</h2>
      <p class="text-base opacity-60">{{ $t('views.auth.ya.redirecting') }}</p>
    </div>
  </div>
</template>
