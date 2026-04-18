<script setup lang="ts">
defineProps<{
  confirmTitle: string
  confirmHint: string
  showLinkConfirmDrawer: boolean
  handleLinkAccept: () => void
  handleLinkDecline: () => void
}>()
</script>

<template>
    <div
      class="modal modal-bottom sm:modal-middle"
      :class="{ 'modal-open': showLinkConfirmDrawer }"
    >
      <div class="modal-box p-0 bg-base-100">
        <div class="px-5 pt-5 pb-4 flex flex-col items-center text-center">
          <h3 class="font-bold text-lg mb-1 w-full text-center">{{ confirmTitle }}</h3>
          <p class="text-sm opacity-60 mb-5 w-full text-center">{{ confirmHint }}</p>
          <div class="flex gap-2 w-full justify-center">
            <button class="btn btn-primary flex-1" @click="handleLinkAccept">
              {{ $t('common.yes') }}
            </button>
            <button class="btn btn-ghost flex-1" @click="handleLinkDecline">
              {{ $t('common.no') }}
            </button>
          </div>
        </div>
      </div>
      <form
        method="dialog"
        class="modal-backdrop bg-black/40 backdrop-blur-[2px]"
        @click="handleLinkDecline"
      >
        <button>close</button>
      </form>
    </div>
</template>