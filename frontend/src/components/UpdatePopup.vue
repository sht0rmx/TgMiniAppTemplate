<script>
import { ref } from 'vue'

const show = ref(false)
let updateSWCallback = null

function update() {
  if (updateSWCallback) updateSWCallback()
  show.value = false
}

function close() {
  show.value = false
}

export function notifyUpdate(updateSW) {
  updateSWCallback = updateSW
  show.value = true
}

export default {
  setup() {
    return { show, update, close }
  },
}
</script>

<template>
  <transition name="slide-up-fade">
    <div v-if="show" class="fixed bottom-6 inset-x-0 flex justify-center z-50 px-4">
      <UAlert
        :title="$t('components.popup.title')"
        :description="$t('components.popup.desc')"
        color="neutral"
        variant="outline"
        :actions="[
          {
            label: $t('components.popup.update'),
            variant: 'solid',
            color: 'accent',
            onClick: update,
          },
          {
            label: $t('components.popup.close'),
            variant: 'subtle',
            color: 'neutral',
            onClick: close,
          },
        ]"
        class="max-w-md w-full"
      />
    </div>
  </transition>
</template>

<style scoped>
.slide-up-fade-enter-active,
.slide-up-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-up-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.slide-up-fade-enter-to {
  opacity: 1;
  transform: translateY(0);
}
.slide-up-fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}
.slide-up-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
