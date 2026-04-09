<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  code: string
  isOpen: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const copied = ref(false)

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  } catch (err) {
    console.error('Failed to copy: ', err)
  }
}

const closeModal = () => {
  emit('close')
}
</script>

<template>
  <div v-if="isOpen" class="modal modal-open" role="dialog">
    <div class="modal-box">
      <h3 class="text-lg font-bold">{{ $t('views.auth.recovery_code_title') }}</h3>
      <p class="py-4">{{ $t('views.auth.recovery_code_description') }}</p>
      <div class="bg-base-200 p-4 rounded-lg">
        <code class="text-lg font-mono">{{ code }}</code>
      </div>
      <p class="py-2 text-sm opacity-60">{{ $t('views.auth.recovery_code_warning') }}</p>
      <div class="modal-action">
        <button class="btn btn-primary" @click="copyCode">
          <span v-if="copied" class="ri-check-line"></span>
          <span v-else class="ri-file-copy-line"></span>
          {{ copied ? $t('common.copied') : $t('common.copy') }}
        </button>
        <button class="btn" @click="closeModal">{{ $t('common.close') }}</button>
      </div>
    </div>
  </div>
</template>