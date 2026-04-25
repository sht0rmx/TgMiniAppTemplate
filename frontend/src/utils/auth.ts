import { PingService } from '@/utils/api/ping.api.ts'
import { isTgEnv, unableAccessApi } from '@/main.ts'
import { apiClient } from '@/utils/api/api.ts'
import { AuthService } from '@/utils/api/auth.api.ts'
import router from '@/utils/router.ts'
import { showPush } from '@/utils/alert'
import { showRecoveryCodeModal } from '@/main'
import type { Router } from 'vue-router'

export async function authInit(): Promise<boolean> {
  let res = await PingService.pingPong()
  if (!res) {
    unableAccessApi.value = true
    return false
  }

  let ac = apiClient.getAccessToken()

  if (ac) {
    return await AuthService.check()
  }

  if (router.currentRoute.value.path === '/' || isTgEnv.value) {
    await router.push({
      path: '/login',
      query: {
        redirect: router.currentRoute.value.path,
      },
    })
  } else {
    if (router.currentRoute.value.path !== '/login') {
      showPush('views.auth.without_login', '', 'alert-warning', 'ri-error-warning-line')
    }
  }

  return false
}

export async function syncSessionThenNavigate(
  router: Router,
  redirectPath: string,
): Promise<boolean> {
  const ok = await AuthService.check()
  if (ok) {
    await router.push(redirectPath)
  }
  return ok
}

export async function finalizeAuthAndRedirect(
  router: Router,
  redirectPath: string,
  options?: { recoveryCode?: string | null },
): Promise<boolean> {
  if (options?.recoveryCode) {
    showRecoveryCodeModal(options.recoveryCode)
  }
  return syncSessionThenNavigate(router, redirectPath)
}
