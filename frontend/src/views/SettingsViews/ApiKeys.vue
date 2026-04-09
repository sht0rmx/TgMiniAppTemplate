<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { type ApiKey, ApiKeysService } from '@/utils/api/apikeys.api.ts'
import { showPush } from '@/components/alert'
import Header from '@/components/Header.vue'
import Menu from '@/components/menu/Menu.vue'
import MenuButton from '@/components/menu/Button.vue'

const keys = ref<ApiKey[]>([])
const isLoading = ref(true)

// create dialog
const showCreateDialog = ref(false)
const newKeyName = ref('')
const isCreating = ref(false)

// created key reveal
const showRevealDialog = ref(false)
const revealedKey = ref('')
const revealedName = ref('')
const copied = ref(false)

// detail drawer
const selectedKey = ref<ApiKey | null>(null)
const drawerOpen = ref(false)

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

async function loadKeys() {
  isLoading.value = true
  try {
    keys.value = await ApiKeysService.getAll()
  } catch (e) {
    console.error('Failed to load API keys', e)
  } finally {
    isLoading.value = false
  }
}

// Create
function openCreateDialog() {
  newKeyName.value = ''
  showCreateDialog.value = true
}

function closeCreateDialog() {
  showCreateDialog.value = false
  newKeyName.value = ''
}

async function createKey() {
  const name = newKeyName.value.trim()
  if (!name) return

  isCreating.value = true
  try {
    const res = await ApiKeysService.create(name)
    if (res) {
      revealedKey.value = res.key
      revealedName.value = res.name
      copied.value = false
      closeCreateDialog()
      showRevealDialog.value = true
      await loadKeys()
    } else {
      showPush('views.api_keys.create_failed', '', 'alert-warning', 'ri-error-warning-line')
    }
  } catch {
    showPush('views.api_keys.create_failed', '', 'alert-warning', 'ri-error-warning-line')
  } finally {
    isCreating.value = false
  }
}

function closeRevealDialog() {
  showRevealDialog.value = false
  revealedKey.value = ''
  revealedName.value = ''
}

async function copyKey() {
  try {
    await navigator.clipboard.writeText(revealedKey.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    /* fallback: select text */
  }
}

// Detail drawer
function openDrawer(key: ApiKey) {
  selectedKey.value = { ...key }
  drawerOpen.value = true
}

function closeDrawer() {
  drawerOpen.value = false
  selectedKey.value = null
}

async function toggleBan() {
  if (!selectedKey.value) return
  const result = await ApiKeysService.toggleBan(selectedKey.value.id)
  if (result !== null) {
    selectedKey.value.banned = result
    const idx = keys.value.findIndex((k) => k.id === selectedKey.value?.id)

    if (idx !== -1 && keys.value[idx]) {
      keys.value[idx].banned = result
    }
  } else {
    showPush('views.api_keys.action_failed', '', 'alert-warning', 'ri-error-warning-line')
  }
}

async function deleteKey() {
  if (!selectedKey.value) return
  const ok = await ApiKeysService.remove(selectedKey.value.id)
  if (ok) {
    keys.value = keys.value.filter((k) => k.id !== selectedKey.value?.id)
    showPush('views.api_keys.deleted', '', 'alert-success', 'ri-check-line')
  } else {
    showPush('views.api_keys.action_failed', '', 'alert-warning', 'ri-error-warning-line')
  }
  closeDrawer()
}

onMounted(() => loadKeys())
</script>

<template>
  <Header :title="$t('views.api_keys.title')" />

  <div class="flex flex-col max-w-xl mx-auto space-y-8 text-base-content">
    <!-- Hero -->
    <div class="text-center space-y-3 mb-3">
      <i class="ri-key-2-line text-8xl text-accent"></i>
      <p class="text-sm text-muted-foreground max-w-sm mx-auto">
        {{ $t('views.api_keys.hint') }}
      </p>
    </div>

    <!-- Create button -->
    <button
      class="btn btn-soft btn-accent w-full py-6 flex items-center justify-center gap-2"
      @click="openCreateDialog"
    >
      <i class="ri-add-line text-xl"></i>
      <span class="font-semibold">{{ $t('views.api_keys.create') }}</span>
    </button>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <template v-else>
      <!-- Keys list -->
      <div class="space-y-2">
        <h3 class="text-sm font-semibold text-muted-foreground px-2">
          {{ $t('views.api_keys.active_keys') }}
        </h3>

        <div v-if="keys.length === 0" class="text-center py-6 opacity-50">
          <i class="ri-key-2-line text-4xl mb-2 block"></i>
          <p class="text-sm">{{ $t('views.api_keys.empty') }}</p>
        </div>

        <Menu v-else>
          <MenuButton
            v-for="k in keys"
            :key="k.id"
            :text="k.name"
            icon="ri-key-2-line"
            @click="openDrawer(k)"
          >
            <template #content>
              <div class="w-full flex items-center gap-3">
                <i
                  class="ri-key-2-line text-2xl"
                  :class="k.banned ? 'text-error opacity-50' : 'text-accent'"
                ></i>
                <div class="flex-1 text-left">
                  <div class="font-medium" :class="{ 'line-through opacity-50': k.banned }">
                    {{ k.name }}
                  </div>
                  <div class="text-xs text-muted-foreground">
                    sk_•••• · {{ formatDate(k.createdAt) }}
                  </div>
                </div>
                <span v-if="k.banned" class="badge badge-error badge-sm">
                  {{ $t('views.api_keys.banned_badge') }}
                </span>
                <i v-else class="ri-arrow-right-s-line text-lg opacity-60"></i>
              </div>
            </template>
          </MenuButton>
        </Menu>
      </div>
    </template>

    <!-- Key detail drawer -->
    <div class="modal modal-bottom sm:modal-middle" :class="{ 'modal-open': drawerOpen }">
      <div
        class="modal-box p-0 bg-base-100 rounded-t-3xl sm:rounded-3xl border-t sm:border-t-0 border-base-300"
      >
        <div class="px-5 pt-5 pb-4 flex flex-col items-center text-center">
          <div class="flex items-center gap-3 w-full mb-3">
            <div
              class="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0"
              :class="selectedKey?.banned ? 'bg-error/10 text-error' : 'bg-accent/10 text-accent'"
            >
              <i class="ri-key-2-line text-2xl"></i>
            </div>
            <div class="text-left flex-1 min-w-0">
              <h3 class="text-lg font-bold leading-tight truncate">{{ selectedKey?.name }}</h3>
              <p class="text-xs opacity-50 font-mono">sk_••••••••</p>
            </div>
            <span v-if="selectedKey?.banned" class="badge badge-error badge-sm shrink-0">
              {{ $t('views.api_keys.banned_badge') }}
            </span>
          </div>

          <div class="grid grid-cols-1 gap-2 w-full mb-4">
            <div class="flex items-center justify-between px-3 py-2.5 bg-base-200 rounded-xl">
              <span class="text-xs opacity-60">{{ $t('views.api_keys.detail.created') }}</span>
              <span class="text-xs font-medium">
                {{ selectedKey ? formatDate(selectedKey.createdAt) : '' }}
              </span>
            </div>
            <div class="flex items-center justify-between px-3 py-2.5 bg-base-200 rounded-xl">
              <span class="text-xs opacity-60">{{ $t('views.api_keys.detail.status') }}</span>
              <span
                class="text-xs font-medium"
                :class="selectedKey?.banned ? 'text-error' : 'text-success'"
              >
                {{
                  selectedKey?.banned
                    ? $t('views.api_keys.detail.disabled')
                    : $t('views.api_keys.detail.active')
                }}
              </span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 w-full">
            <button
              class="btn rounded-xl"
              :class="selectedKey?.banned ? 'btn-success' : 'btn-warning'"
              @click="toggleBan"
            >
              <i :class="selectedKey?.banned ? 'ri-lock-unlock-line' : 'ri-lock-line'"></i>
              {{
                selectedKey?.banned
                  ? $t('views.api_keys.detail.enable')
                  : $t('views.api_keys.detail.disable')
              }}
            </button>
            <button class="btn btn-error rounded-xl" @click="deleteKey">
              <i class="ri-delete-bin-line"></i>
              {{ $t('views.api_keys.detail.delete') }}
            </button>
          </div>
        </div>
      </div>
      <form
        method="dialog"
        class="modal-backdrop bg-black/40 backdrop-blur-[2px]"
        @click="closeDrawer"
      >
        <button>close</button>
      </form>
    </div>

    <!-- Create dialog -->
    <div class="modal" :class="{ 'modal-open': showCreateDialog }">
      <div class="modal-box max-w-sm">
        <h3 class="font-bold text-lg mb-1">{{ $t('views.api_keys.create_dialog.title') }}</h3>
        <p class="text-sm opacity-60 mb-5">{{ $t('views.api_keys.create_dialog.hint') }}</p>

        <div class="flex flex-col gap-3">
          <label class="input input-bordered w-full flex items-center gap-2">
            <i class="ri-price-tag-3-line opacity-50"></i>
            <input
              v-model="newKeyName"
              type="text"
              class="grow"
              :placeholder="$t('views.api_keys.create_dialog.placeholder')"
              maxlength="30"
              @keyup.enter="createKey"
            />
          </label>
          <button
            class="btn btn-primary w-full"
            :disabled="!newKeyName.trim() || isCreating"
            @click="createKey"
          >
            <span v-if="isCreating" class="loading loading-spinner loading-sm"></span>
            <i v-else class="ri-add-line"></i>
            {{ $t('views.api_keys.create') }}
          </button>
        </div>

        <div class="modal-action mt-3">
          <button class="btn btn-ghost w-full" @click="closeCreateDialog">
            {{ $t('views.api_keys.close') }}
          </button>
        </div>
      </div>
      <form
        method="dialog"
        class="modal-backdrop bg-black/40 backdrop-blur-[2px]"
        @click="closeCreateDialog"
      >
        <button>close</button>
      </form>
    </div>

    <!-- Reveal key dialog -->
    <div class="modal" :class="{ 'modal-open': showRevealDialog }">
      <div class="modal-box max-w-sm">
        <div class="flex flex-col items-center text-center">
          <div
            class="w-16 h-16 mb-4 rounded-2xl bg-success/10 flex items-center justify-center text-success"
          >
            <i class="ri-check-double-line text-4xl"></i>
          </div>

          <h3 class="font-bold text-lg mb-1">{{ $t('views.api_keys.reveal.title') }}</h3>
          <p class="text-sm opacity-60 mb-5">{{ $t('views.api_keys.reveal.hint') }}</p>

          <div
            class="w-full p-4 bg-base-200 rounded-2xl font-mono text-sm break-all text-left select-all cursor-pointer mb-4"
            @click="copyKey"
          >
            {{ revealedKey }}
          </div>

          <button class="btn btn-soft btn-accent w-full gap-2 mb-2" @click="copyKey">
            <i :class="copied ? 'ri-check-line' : 'ri-file-copy-line'"></i>
            {{ copied ? $t('views.api_keys.reveal.copied') : $t('views.api_keys.reveal.copy') }}
          </button>

          <button class="btn btn-ghost w-full" @click="closeRevealDialog">
            {{ $t('views.api_keys.close') }}
          </button>
        </div>
      </div>
      <form
        method="dialog"
        class="modal-backdrop bg-black/40 backdrop-blur-[2px]"
        @click="closeRevealDialog"
      >
        <button>close</button>
      </form>
    </div>
  </div>
</template>
