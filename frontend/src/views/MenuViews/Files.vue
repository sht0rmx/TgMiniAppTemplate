<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { FilesService, type FileItem } from '@/utils/api/files.api.ts'
import { showPush } from '@/components/alert'
import Header from '@/components/Header.vue'
import Menu from '@/components/menu/Menu.vue'
import MenuButton from '@/components/menu/Button.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'

const MAX_NAME_LEN = 28

const files = ref<FileItem[]>([])
const isLoading = ref(true)
const isUploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

// Detail drawer
const selectedFile = ref<FileItem | null>(null)
const drawerOpen = ref(false)
const isRenaming = ref(false)
const renameInput = ref('')

// Preview
const previewOpen = ref(false)
const previewUrl = ref('')
const previewType = ref<'image' | 'video' | 'pdf' | 'text' | 'audio' | 'unknown'>('unknown')
const previewText = ref('')
const isPreviewLoading = ref(false)

const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico']
const videoExts = ['mp4', 'webm', 'ogg', 'mov']
const audioExts = ['mp3', 'wav', 'flac', 'aac', 'm4a', 'opus', 'weba']
const textExts = [
  'txt',
  'md',
  'json',
  'csv',
  'xml',
  'html',
  'css',
  'js',
  'ts',
  'py',
  'log',
  'yml',
  'yaml',
  'toml',
  'ini',
  'env',
  'sh',
]

function getExt(name: string): string {
  const dot = name.lastIndexOf('.')
  return dot !== -1 ? name.substring(dot + 1).toLowerCase() : ''
}

function getFileIcon(name: string): string {
  const ext = getExt(name)
  if (imageExts.includes(ext)) return 'ri-image-line'
  if (videoExts.includes(ext)) return 'ri-video-line'
  if (audioExts.includes(ext)) return 'ri-music-2-line'
  if (ext === 'pdf') return 'ri-file-pdf-2-line'
  if (textExts.includes(ext)) return 'ri-file-text-line'
  return 'ri-file-line'
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function formatName(name: string): string {
  // strip UUID prefix (uuid-filename)
  const dashIdx = name.indexOf('-')
  if (dashIdx > 30) name = name.substring(dashIdx + 1)

  if (name.length <= MAX_NAME_LEN) return name

  const dot = name.lastIndexOf('.')
  if (dot === -1) return name.substring(0, MAX_NAME_LEN - 1) + '…'

  const ext = name.substring(dot)
  const base = name.substring(0, dot)
  const maxBase = MAX_NAME_LEN - ext.length - 1
  if (maxBase < 4) return name.substring(0, MAX_NAME_LEN - 1) + '…'

  return base.substring(0, maxBase) + '…' + ext
}

const sortedFiles = computed(() =>
  [...files.value].sort(
    (a, b) => new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime(),
  ),
)

async function loadFiles() {
  isLoading.value = true
  try {
    files.value = await FilesService.getAll()
  } catch (e) {
    console.error('Failed to load files', e)
  } finally {
    isLoading.value = false
  }
}

function triggerUpload() {
  fileInput.value?.click()
}

async function onFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  if (file.size > 10 * 1024 * 1024) {
    showPush('views.files.too_large', '', 'alert-warning', 'ri-error-warning-line')
    return
  }

  isUploading.value = true
  try {
    const ok = await FilesService.upload(file)
    if (ok) {
      showPush('views.files.uploaded', '', 'alert-success', 'ri-check-line')
      await loadFiles()
    } else {
      showPush('views.files.upload_failed', '', 'alert-warning', 'ri-error-warning-line')
    }
  } catch {
    showPush('views.files.upload_failed', '', 'alert-warning', 'ri-error-warning-line')
  } finally {
    isUploading.value = false
    target.value = ''
  }
}

function openDrawer(file: FileItem) {
  selectedFile.value = { ...file }
  renameInput.value = file.name
  isRenaming.value = false
  drawerOpen.value = true
}

function closeDrawer() {
  drawerOpen.value = false
  selectedFile.value = null
}

async function previewFile() {
  if (!selectedFile.value) return

  isPreviewLoading.value = true
  try {
    const b = await FilesService.getBlob(selectedFile.value.id)
    if (!b) {
      showPush('views.files.preview_failed', '', 'alert-warning', 'ri-error-warning-line')
      return
    }

    const ext = getExt(selectedFile.value.name)
    previewUrl.value = URL.createObjectURL(b)

    if (audioExts.includes(ext)) previewType.value = 'audio'
    else if (videoExts.includes(ext)) previewType.value = 'video'
    else if (imageExts.includes(ext)) previewType.value = 'image'
    else if (ext === 'pdf') previewType.value = 'pdf'
    else if (textExts.includes(ext)) {
      previewType.value = 'text'
      previewText.value = await b.text()
    } else {
      previewType.value = 'unknown'
    }

    previewOpen.value = true
    closeDrawer()
  } catch {
    showPush('views.files.preview_failed', '', 'alert-warning', 'ri-error-warning-line')
  } finally {
    isPreviewLoading.value = false
  }
}

function closePreview() {
  previewOpen.value = false
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
  previewText.value = ''
}

async function downloadFile() {
  if (!selectedFile.value) return
  const ok = await FilesService.download(selectedFile.value.id, formatName(selectedFile.value.name))
  if (!ok) {
    showPush('views.files.download_failed', '', 'alert-warning', 'ri-error-warning-line')
  }
}

async function deleteFile() {
  if (!selectedFile.value) return
  const ok = await FilesService.remove(selectedFile.value.id)
  if (ok) {
    files.value = files.value.filter((f) => f.id !== selectedFile.value?.id)
    showPush('views.files.deleted', '', 'alert-success', 'ri-check-line')
  } else {
    showPush('views.files.delete_failed', '', 'alert-warning', 'ri-error-warning-line')
  }
  closeDrawer()
}

async function submitRename() {
  if (!selectedFile.value || !renameInput.value.trim()) return

  const oldName = selectedFile.value.name
  const newName = renameInput.value.trim()

  if (oldName === newName) {
    isRenaming.value = false
    return
  }

  try {
    if (!selectedFile.value) return
    const ok = await FilesService.rename(selectedFile.value.id, newName)
    if (ok && selectedFile.value) {
      selectedFile.value.name = newName
      const fileIdx = files.value.findIndex((f) => f.id === selectedFile.value?.id)
      if (fileIdx !== -1 && files.value[fileIdx]) {
        files.value[fileIdx].name = newName
      }
      showPush('views.files.renamed', '', 'alert-success', 'ri-check-line')
      isRenaming.value = false
    } else {
      showPush('views.files.rename_failed', '', 'alert-warning', 'ri-error-warning-line')
    }
  } catch {
    showPush('views.files.rename_failed', '', 'alert-warning', 'ri-error-warning-line')
  }
}

function cancelRename() {
  if (selectedFile.value) {
    renameInput.value = selectedFile.value.name
  }
  isRenaming.value = false
}

onMounted(() => loadFiles())
</script>

<template>
  <Header :title="$t('views.files.title')" />

  <div class="flex flex-col max-w-xl mx-auto space-y-6 text-base-content p-4">
    <!-- Hero -->
    <div class="text-center space-y-3 mb-2">
      <i class="ri-folder-3-line text-8xl text-accent"></i>
      <p class="text-sm opacity-60 max-w-sm mx-auto">
        {{ $t('views.files.hint') }}
      </p>
    </div>

    <!-- Upload button -->
    <input ref="fileInput" type="file" class="hidden" @change="onFileSelected" />
    <button
      class="btn btn-soft btn-accent w-full py-6 flex items-center justify-center gap-2"
      :disabled="isUploading"
      @click="triggerUpload"
    >
      <span v-if="isUploading" class="loading loading-spinner loading-sm"></span>
      <i v-else class="ri-upload-2-line text-xl"></i>
      <span class="font-semibold">{{ $t('views.files.upload') }}</span>
    </button>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <template v-else>
      <div class="space-y-2">
        <h3 class="text-sm font-semibold opacity-60 px-2">
          {{ $t('views.files.your_files') }}
        </h3>

        <div v-if="files.length === 0" class="text-center py-6 opacity-50">
          <i class="ri-folder-line text-4xl mb-2 block"></i>
          <p class="text-sm">{{ $t('views.files.empty') }}</p>
        </div>

        <Menu v-else>
          <MenuButton
            v-for="f in sortedFiles"
            :key="f.id"
            :text="formatName(f.name)"
            :icon="getFileIcon(f.name)"
            @click="openDrawer(f)"
          >
            <template #content>
              <div class="w-full flex items-center gap-3">
                <i :class="getFileIcon(f.name)" class="text-2xl text-accent shrink-0"></i>
                <div class="flex-1 text-left min-w-0">
                  <div class="font-medium truncate text-sm">{{ formatName(f.name) }}</div>
                  <div class="text-xs opacity-50">{{ formatDate(f.uploadedAt) }}</div>
                </div>
                <i class="ri-arrow-right-s-line text-lg opacity-60 shrink-0"></i>
              </div>
            </template>
          </MenuButton>
        </Menu>
      </div>
    </template>

    <!-- File detail drawer -->
    <div class="modal modal-bottom sm:modal-middle" :class="{ 'modal-open': drawerOpen }">
      <div
        class="modal-box p-0 bg-base-100 rounded-t-3xl sm:rounded-3xl border-t sm:border-t-0 border-base-300"
      >
        <div class="px-5 pt-5 pb-4 flex flex-col items-center text-center">
          <div class="flex items-center gap-3 w-full mb-3">
            <div
              class="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 bg-accent/10 text-accent"
            >
              <i
                :class="selectedFile ? getFileIcon(selectedFile.name) : 'ri-file-line'"
                class="text-2xl"
              ></i>
            </div>
            <div class="text-left flex-1 min-w-0">
              <div v-if="!isRenaming" class="flex items-center gap-2">
                <h3 class="text-lg font-bold leading-tight truncate">
                  {{ selectedFile ? formatName(selectedFile.name) : '' }}
                </h3>
                <button
                  class="btn btn-ghost btn-xs btn-circle"
                  @click="isRenaming = true"
                  :disabled="isPreviewLoading"
                >
                  <i class="ri-edit-line text-sm"></i>
                </button>
              </div>
              <div v-else class="space-y-2">
                <input
                  v-model="renameInput"
                  type="text"
                  class="input input-sm input-bordered w-full"
                  @keydown.enter="submitRename"
                  @keydown.escape="cancelRename"
                  autofocus
                />
                <div class="flex gap-2 justify-end">
                  <button class="btn btn-sm btn-ghost" @click="cancelRename">
                    {{ $t('views.files.cancel') }}
                  </button>
                  <button class="btn btn-sm btn-primary" @click="submitRename">
                    {{ $t('views.files.save') }}
                  </button>
                </div>
              </div>
              <p class="text-xs opacity-50 font-mono truncate">
                .{{ selectedFile ? getExt(selectedFile.name) : '' }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-2 w-full mb-4">
            <div class="flex items-center justify-between px-3 py-2.5 bg-base-200 rounded-xl">
              <span class="text-xs opacity-60">{{ $t('views.files.detail.uploaded') }}</span>
              <span class="text-xs font-medium">
                {{ selectedFile ? formatDate(selectedFile.uploadedAt) : '' }}
              </span>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2 w-full">
            <button
              class="btn btn-primary rounded-xl"
              :disabled="isPreviewLoading"
              @click="previewFile"
            >
              <span v-if="isPreviewLoading" class="loading loading-spinner loading-xs"></span>
              <i v-else class="ri-eye-line"></i>
              {{ $t('views.files.detail.preview') }}
            </button>
            <button class="btn btn-accent rounded-xl" @click="downloadFile">
              <i class="ri-download-line"></i>
              {{ $t('views.files.detail.download') }}
            </button>
            <button class="btn btn-error rounded-xl" @click="deleteFile">
              <i class="ri-delete-bin-line"></i>
              {{ $t('views.files.detail.delete') }}
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

    <!-- Preview modal -->
    <div class="modal modal-bottom sm:modal-middle" :class="{ 'modal-open': previewOpen }">
      <div class="modal-box max-w-2xl max-h-[85vh] bg-base-100 rounded-t-3xl sm:rounded-3xl p-0">
        <!-- Preview header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-base-300">
          <h3 class="font-semibold text-sm truncate">{{ $t('views.files.detail.preview') }}</h3>
          <button class="btn btn-ghost btn-sm btn-circle" @click="closePreview">
            <i class="ri-close-line text-lg"></i>
          </button>
        </div>

        <!-- Preview content -->
        <div class="p-4 overflow-auto max-h-[calc(85vh-4rem)] flex items-center justify-center">
          <!-- Image -->
          <img
            v-if="previewType === 'image'"
            :src="previewUrl"
            alt="preview"
            class="max-w-full max-h-[70vh] rounded-lg object-contain"
          />

          <!-- Video -->
          <video
            v-else-if="previewType === 'video'"
            :src="previewUrl"
            controls
            class="max-w-full max-h-[70vh] rounded-lg"
          ></video>

          <!-- Audio -->
          <div v-else-if="previewType === 'audio'" class="w-full max-w-md px-4">
            <AudioPlayer :src="previewUrl" :title="selectedFile?.name || 'Audio'" />
          </div>

          <!-- PDF -->
          <iframe
            v-else-if="previewType === 'pdf'"
            :src="previewUrl"
            class="w-full h-[70vh] rounded-lg border-0"
          ></iframe>

          <!-- Text -->
          <pre
            v-else-if="previewType === 'text'"
            class="w-full text-sm bg-base-200 p-4 rounded-xl overflow-auto max-h-[70vh] whitespace-pre-wrap font-mono"
            >{{ previewText }}</pre
          >

          <!-- Unknown -->
          <div v-else class="text-center py-12 opacity-50">
            <i class="ri-file-unknow-line text-5xl mb-3 block"></i>
            <p class="text-sm">{{ $t('views.files.preview_unsupported') }}</p>
          </div>
        </div>
      </div>
      <form
        method="dialog"
        class="modal-backdrop bg-black/40 backdrop-blur-[2px]"
        @click="closePreview"
      >
        <button>close</button>
      </form>
    </div>
  </div>
</template>
