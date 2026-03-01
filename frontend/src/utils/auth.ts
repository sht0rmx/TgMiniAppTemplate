import { PingService } from '@/utils/api/ping.api.ts'
import { isTgEnv, unableAccessApi } from '@/main.ts'
import { apiClient } from '@/utils/api/api.ts'
import { AuthService } from '@/utils/api/auth.api.ts'
import router from '@/utils/router.ts'
import { showPush } from '@/components/alert'

export async function authInit(): Promise<boolean> {
  let res = await PingService.pingPong()
  if (!res) {
    unableAccessApi.value = true
    return false
  }

  let ac = apiClient.getAccessToken()
  if (!ac) {
    try {
      const refreshed = await apiClient.refreshTokens()
      if (refreshed) {
        ac = apiClient.getAccessToken()
      }
    } catch {}
  }

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
    showPush('views.auth.without_login', '', 'alert-warning', 'ri-error-warning-line')
  }

  return false
}