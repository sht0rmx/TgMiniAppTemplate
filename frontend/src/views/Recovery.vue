<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { AuthService } from '@/utils/api/auth.api'
import { showPush } from '@/components/alert'
import { authStatus } from '@/main'

const router = useRouter()

const recoveryCode = ref('')
const isSubmitting = ref(false)

const submitRecovery = async () => {
  if (!recoveryCode.value.trim()) {
    showPush('views.recovery.code_required', '', 'alert-warning', 'ri-error-warning-line')
    return
  }

  if (!authStatus.value) {
    showPush('views.recovery.auth_required', '', 'alert-warning', 'ri-close-line')
    return
  }

  isSubmitting.value = true

  try {
    const success = await AuthService.transferAccount({ recovery_code: recoveryCode.value })
    if (success) {
      showPush('views.recovery.success', '', 'alert-success', 'ri-check-line')
      router.push('/')
    } else {
      showPush('views.recovery.failed', '', 'alert-warning', 'ri-close-line')
    }
  } catch (error) {
    showPush('views.recovery.error', '', 'alert-warning', 'ri-close-line')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-4">
    <div class="card w-full max-w-md bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title">{{ $t('views.recovery.title') }}</h2>
        <p class="text-sm opacity-60">{{ $t('views.recovery.description') }}</p>

        <fieldset class="fieldset">
          <legend class="fieldset-legend">{{ $t('views.recovery.code_label') }}</legend>
          <input
            v-model="recoveryCode"
            type="text"
            placeholder="XXXX-XXXX-XXXX-XXXX"
            class="input input-bordered"
            :disabled="isSubmitting"
          />
        </fieldset>

        <div class="card-actions justify-end mt-4">
          <button
            class="btn btn-primary"
            :disabled="isSubmitting || !recoveryCode.trim()"
            @click="submitRecovery"
          >
            <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
            {{ $t('views.recovery.submit') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
