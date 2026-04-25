<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { Html5Qrcode } from 'html5-qrcode'
import { SessionsService, type Session } from '@/utils/api/sessions.api.ts'
import { AuthService } from '@/utils/api/auth.api.ts'
import { showPush } from '@/utils/alert'
import Menu from '@/components/menu/Menu.vue'
import MenuButton from '@/components/menu/Button.vue'
import Header from '@/components/Header.vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const sessions = ref<Session[]>([])
const currentSession = ref<Session | null>(null)
const otherSessions = ref<Session[]>([])

const selectedSession = ref<Session | null>(null)
const drawerOpen = ref(false)

const showScanner = ref(false)
const showLinkDialog = ref(false)
const codeInput = ref('')
const isAccepting = ref(false)
const isLoadingSessions = ref(true)

const showQrConfirm = ref(false)
const scannedLoginId = ref<string | null>(null)

let scanner: Html5Qrcode | null = null

function getDeviceIcon(info: Session['info']): string {
  const sys = (info.system || '').toLowerCase()
  if (sys.includes('android')) return 'ri-android-line'
  if (sys.includes('ios') || sys.includes('iphone') || sys.includes('ipad')) return 'ri-apple-line'
  if (sys.includes('mac')) return 'ri-macbook-line'
  if (sys.includes('windows')) return 'ri-windows-line'
  if (sys.includes('linux')) return 'ri-ubuntu-line'
  return 'ri-device-line'
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleString()
  } catch {
    return iso
  }
}

async function loadSessions() {
  isLoadingSessions.value = true
  try {
    const data = await SessionsService.getAllSessions()
    sessions.value = data.sessions
    currentSession.value = data.sessions.find((s) => s.isCurrent) || null
    otherSessions.value = data.sessions.filter((s) => !s.isCurrent)
  } catch (e) {
    console.error('Failed to load sessions', e)
  } finally {
    isLoadingSessions.value = false
  }
}

const openLinkDialog = () => {
  codeInput.value = ''
  showLinkDialog.value = true
}

const closeLinkDialog = () => {
  showLinkDialog.value = false
  codeInput.value = ''
}

const handleStartScanner = () => {
  closeLinkDialog()
  startScanner()
}

const startScanner = async () => {
  showScanner.value = true
  await nextTick()
  if (!scanner) scanner = new Html5Qrcode('scanner')
  try {
    await scanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: 250 },
      handleScan,
      () => { },
    )
  } catch (err) {
    console.error('Failed to start scanner', err)
  }
}

const stopScanner = async () => {
  showScanner.value = false
  if (scanner) {
    await scanner.stop().catch(console.error)
    scanner.clear()
    scanner = null
  }
}

const handleScan = async (decodedText: string) => {
  try {
    const url = new URL(decodedText)
    const loginid = url.searchParams.get('loginid')

    if (loginid) {
      const loginId = atob(loginid)
      await stopScanner()
      scannedLoginId.value = loginId
      showQrConfirm.value = true
    }
  } catch (e) {
    console.warn('QR parse error', e)
  }
}

const handleQrAccept = async () => {
  if (!scannedLoginId.value) return
  isAccepting.value = true
  try {
    const ok = await AuthService.acceptRemoteLogin(scannedLoginId.value)
    if (ok) {
      showPush('views.devices.accept_success', '', 'alert-success', 'ri-check-line')
      showQrConfirm.value = false
      scannedLoginId.value = null
    } else {
      showPush('views.devices.accept_failed', '', 'alert-warning', 'ri-error-warning-line')
    }
  } catch {
    showPush('views.devices.accept_failed', '', 'alert-warning', 'ri-error-warning-line')
  } finally {
    isAccepting.value = false
  }
}

const handleQrDecline = () => {
  showQrConfirm.value = false
  scannedLoginId.value = null
}

const acceptByCode = async () => {
  const code = codeInput.value.trim().toLowerCase()
  if (!code) return

  isAccepting.value = true
  try {
    const ok = await AuthService.acceptByCode(code)
    if (ok) {
      showPush('views.devices.accept_success', '', 'alert-success', 'ri-check-line')
      closeLinkDialog()
    } else {
      showPush('views.devices.accept_failed', '', 'alert-warning', 'ri-error-warning-line')
    }
  } catch {
    showPush('views.devices.accept_failed', '', 'alert-warning', 'ri-error-warning-line')
  } finally {
    isAccepting.value = false
  }
}

const openDrawer = (session: Session) => {
  selectedSession.value = session
  drawerOpen.value = true
}

const closeDrawer = () => {
  drawerOpen.value = false
  selectedSession.value = null
}

const terminateSession = async () => {
  if (!selectedSession.value) return

  try {
    const ok = await SessionsService.killSession(selectedSession.value.id)
    if (ok) {
      otherSessions.value = otherSessions.value.filter((s) => s.id !== selectedSession.value?.id)
      showPush('views.devices.session_killed', '', 'alert-success', 'ri-check-line')
    } else {
      showPush('views.devices.kill_failed', '', 'alert-warning', 'ri-error-warning-line')
    }
  } catch {
    showPush('views.devices.kill_failed', '', 'alert-warning', 'ri-error-warning-line')
  } finally {
    closeDrawer()
  }
}

function parseLoginIdFromQuery() {
  const raw = route.query.loginid
  if (!raw || typeof raw !== 'string') return null

  try {
    return window.location.origin + route.fullPath
  } catch {
    return null
  }
}

onMounted(() => {
  loadSessions()
  handleScan(parseLoginIdFromQuery() as string)
})

onUnmounted(() => stopScanner())
</script>

<template>
  <Header :title="$t('views.devices.title')" />
  <div class="flex flex-col max-w-xl mx-auto space-y-8 text-base-content">
    <div class="text-center space-y-3 mb-3">
      <i class="ri-mac-line text-8xl text-accent"></i>
      <p class="text-sm text-muted-foreground max-w-sm mx-auto">
        {{ $t('views.devices.hint') }}
      </p>
    </div>

    <button class="btn btn-soft btn-accent w-full py-6 flex items-center justify-center gap-2" @click="openLinkDialog">
      <i class="ri-link text-xl"></i>
      <span class="font-semibold">{{ $t('views.devices.link') }}</span>
    </button>

    <div v-if="isLoadingSessions" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <template v-else>
      <div v-if="currentSession" class="space-y-2">
        <h3 class="text-sm font-semibold text-muted-foreground px-2">
          {{ $t('views.devices.this_device') }}
        </h3>
        <Menu>
          <MenuButton :text="currentSession.info.dev || 'Unknown'" :icon="getDeviceIcon(currentSession.info)"
            @click="openDrawer(currentSession)">
            <template #content>
              <div class="w-full flex items-center gap-3">
                <i :class="[getDeviceIcon(currentSession.info), 'text-2xl']"></i>
                <div class="flex-1 text-left">
                  <div class="font-medium">
                    {{ currentSession.info.browser || 'Unknown browser' }}
                  </div>
                  <div class="text-xs text-muted-foreground">
                    {{ currentSession.ip }} · {{ currentSession.info.system }}
                  </div>
                </div>
                <span class="badge badge-success badge-sm">{{
                  $t('views.devices.current_badge')
                  }}</span>
              </div>
            </template>
          </MenuButton>
        </Menu>
      </div>

      <div class="space-y-2">
        <h3 class="text-sm font-semibold text-muted-foreground px-2">
          {{ $t('views.devices.active') }}
        </h3>

        <div v-if="otherSessions.length === 0" class="text-center py-6 opacity-50">
          <i class="ri-device-line text-4xl mb-2 block"></i>
          <p class="text-sm">{{ $t('views.devices.no_devices') }}</p>
        </div>

        <Menu v-else>
          <MenuButton v-for="s in otherSessions" :key="s.id" :text="s.info.dev || 'Unknown'"
            :icon="getDeviceIcon(s.info)" @click="openDrawer(s)">
            <template #content>
              <div class="w-full flex items-center gap-3">
                <i :class="[getDeviceIcon(s.info), 'text-2xl']"></i>
                <div class="flex-1 text-left">
                  <div class="font-medium">{{ s.info.browser || 'Unknown browser' }}</div>
                  <div class="text-xs text-muted-foreground">
                    {{ s.ip }} · {{ formatDate(s.lastUsed) }}
                  </div>
                </div>
                <i class="ri-arrow-right-s-line text-lg opacity-60"></i>
              </div>
            </template>
          </MenuButton>
        </Menu>
      </div>
    </template>
    <Teleport to="body">
      <div class="modal modal-bottom sm:modal-middle" :class="{ 'modal-open': drawerOpen }">
        <div class="modal-box p-0 bg-base-100 rounded-t-3xl sm:rounded-3xl border-t sm:border-t-0 border-base-300">
          <div class="px-5 pt-5 pb-4 flex flex-col items-center text-center">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-12 h-12 rounded-2xl bg-accent/10 flex items-center justify-center text-accent shrink-0">
                <i v-if="selectedSession" :class="getDeviceIcon(selectedSession.info)" class="text-2xl"></i>
              </div>
              <div class="text-left">
                <h3 class="text-lg font-bold leading-tight">
                  {{ selectedSession?.info.browser || 'Unknown' }}
                </h3>
                <p class="text-xs opacity-50">{{ selectedSession?.info.system }}</p>
              </div>
              <span v-if="selectedSession?.isCurrent" class="badge badge-success badge-sm ml-auto">{{
                $t('views.devices.current_badge')
              }}</span>
            </div>

            <div class="grid grid-cols-1 gap-2 w-full mb-4">
              <div class="flex items-center justify-between px-3 py-2.5 bg-base-200 rounded-xl">
                <span class="text-xs opacity-60">{{ $t('views.devices.dropdown.ip') }}</span>
                <span class="font-mono font-medium text-xs">{{ selectedSession?.ip }}</span>
              </div>
              <div class="flex items-center justify-between px-3 py-2.5 bg-base-200 rounded-xl">
                <span class="text-xs opacity-60">{{ $t('views.devices.dropdown.last_seen') }}</span>
                <span class="text-xs font-medium">{{
                  selectedSession ? formatDate(selectedSession.lastUsed) : ''
                }}</span>
              </div>
              <div class="flex items-center justify-between px-3 py-2.5 bg-base-200 rounded-xl">
                <span class="text-xs opacity-60">{{ $t('views.devices.dropdown.created') }}</span>
                <span class="text-xs font-medium">{{
                  selectedSession ? formatDate(selectedSession.createdAt) : ''
                }}</span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2 w-full">
              <button v-if="selectedSession && !selectedSession.isCurrent" class="btn btn-error rounded-xl"
                @click="terminateSession">
                <i class="ri-logout-circle-line"></i>
                {{ $t('views.devices.dropdown.terminate') }}
              </button>
              <button class="btn btn-ghost rounded-xl" :class="{ 'col-span-2': selectedSession?.isCurrent }"
                @click="closeDrawer">
                {{ $t('views.devices.scan.close') }}
              </button>
            </div>
          </div>
        </div>

        <form method="dialog" class="modal-backdrop bg-base-300/60 backdrop-blur-md" @click="closeDrawer">
          <button>close</button>
        </form>
      </div>
    </Teleport>

    <Teleport to="body">
      <div class="modal" :class="{ 'modal-open': showLinkDialog }">
        <div class="modal-box max-w-sm">
          <h3 class="font-bold text-lg mb-1">{{ $t('views.devices.link_dialog.title') }}</h3>
          <p class="text-sm opacity-60 mb-5">{{ $t('views.devices.link_dialog.hint') }}</p>

          <div class="flex flex-col gap-3">
            <button class="btn btn-soft btn-accent w-full flex items-center justify-center gap-2"
              @click="handleStartScanner()">
              <i class="ri-qr-scan-2-line text-lg"></i>
              {{ $t('views.devices.scan.title') }}
            </button>

            <div class="divider text-xs opacity-50 my-0">{{ $t('views.devices.or_code') }}</div>

            <label class="input input-bordered w-full flex items-center gap-2">
              <i class="ri-key-2-line opacity-50"></i>
              <input v-model="codeInput" type="text" class="grow font-mono tracking-wider lowercase"
                :placeholder="$t('views.devices.code_placeholder')" maxlength="8" @keyup.enter="acceptByCode" />
            </label>
            <button class="btn btn-primary w-full" :disabled="!codeInput.trim() || isAccepting" @click="acceptByCode">
              <span v-if="isAccepting" class="loading loading-spinner loading-sm"></span>
              <i v-else class="ri-check-line"></i>
              {{ $t('views.devices.accept_code') }}
            </button>
          </div>

          <div class="modal-action mt-3">
            <button class="btn btn-ghost w-full" @click="closeLinkDialog">
              {{ $t('views.devices.scan.close') }}
            </button>
          </div>
        </div>
        <form method="dialog" class="modal-backdrop bg-base-300/60 backdrop-blur-md" @click="closeLinkDialog">
          <button>close</button>
        </form>
      </div>
    </Teleport>

    <input type="checkbox" class="modal-toggle" v-model="showScanner" />
    <Teleport to="body">
      <div class="modal">
        <div class="modal-box max-w-md flex flex-col items-center">
          <h3 class="font-bold text-lg w-full text-left mb-4">{{ $t('views.devices.scan.title') }}</h3>

          <div class="relative w-full max-w-300px aspect-square p-2 flex items-center justify-center my-2">
            <div
              class="absolute top-0 left-0 w-12 h-12 border-t-4 border-l-4 border-primary rounded-tl-2xl opacity-80 pointer-events-none z-10">
            </div>
            <div
              class="absolute top-0 right-0 w-12 h-12 border-t-4 border-r-4 border-primary rounded-tr-2xl opacity-80 pointer-events-none z-10">
            </div>
            <div
              class="absolute bottom-0 left-0 w-12 h-12 border-b-4 border-l-4 border-primary rounded-bl-2xl opacity-80 pointer-events-none z-10">
            </div>
            <div
              class="absolute bottom-0 right-0 w-12 h-12 border-b-4 border-r-4 border-primary rounded-br-2xl opacity-80 pointer-events-none z-10">
            </div>

            <div id="scanner"
              class="w-full h-full bg-base-300 rounded-xl overflow-hidden shadow-inner flex items-center justify-center">
            </div>
          </div>

          <div class="modal-action w-full mt-6">
            <button class="btn w-full" @click="stopScanner">
              {{ $t('views.devices.scan.close') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div class="modal modal-bottom sm:modal-middle" :class="{ 'modal-open': showQrConfirm }">
        <div class="modal-box bg-base-100 rounded-t-3xl">
          <div class="px-5 pb-4 flex flex-col items-center text-center">
            <h3 class="font-bold text-lg mb-1 w-full text-center">
              {{ $t('views.devices.qr_confirm.title') }}
            </h3>
            <p class="text-sm opacity-60 mb-5 w-full text-center">
              {{ $t('views.devices.qr_confirm.hint') }}
            </p>
            <div class="flex gap-2 w-full justify-center">
              <button class="btn btn-primary flex-1" :disabled="isAccepting" @click="handleQrAccept">
                <span v-if="isAccepting" class="loading loading-spinner loading-sm"></span>
                <span v-else>{{ $t('common.yes') }}</span>
              </button>
              <button class="btn btn-ghost flex-1" :disabled="isAccepting" @click="handleQrDecline">
                {{ $t('common.no') }}
              </button>
            </div>
          </div>
        </div>
        <form method="dialog" class="modal-backdrop bg-base-300/60 backdrop-blur-md" @click="handleQrDecline">
          <button>close</button>
        </form>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
:deep(#scanner__scan_region) {
  border: none !important;
}

:deep(#qr-shaded-region) {
  border-width: 0 !important;
  opacity: 0 !important;
}

:deep(video) {
  object-fit: cover !important;
  width: 100% !important;
  border-radius: 0.75rem;
}
</style>