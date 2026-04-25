<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  isOpen: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  confirmButtonClass?: string
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: 'common.confirm',
  cancelText: 'common.cancel',
  confirmButtonClass: 'btn-error',
  isLoading: false,
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal modal-open" role="dialog">
      <div class="modal-box">
        <h3 class="text-lg font-bold">{{ $t(title) }}</h3>
        <p class="py-4">{{ $t(message) }}</p>
        <div class="modal-action">
          <button class="btn" @click="handleCancel" :disabled="isLoading">
            {{ $t(cancelText) }}
          </button>
          <button :class="['btn', confirmButtonClass]" @click="handleConfirm" :disabled="isLoading">
            <span v-if="isLoading" class="loading loading-spinner loading-sm"></span>
            {{ $t(confirmText) }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
