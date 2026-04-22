<script setup lang="ts">
import { ref } from 'vue'
import { BotService, type SendMessageResponse } from '@/utils/api/bot.api.ts'
import Header from '@/components/Header.vue'
import { showPush } from '@/utils/alert'

const isSending = ref(false)

const handleSend = async () => {
  if (isSending.value) return
  isSending.value = true

  let res = (await BotService.sendMessage('hello my user!!')) as SendMessageResponse
  if (res.detail === 'Message sent') {
    showPush('views.bot.sent', '', 'alert-success', 'ri-check-line')
  } else {
    showPush('views.bot.error', '', 'alert-error', 'ri-error-warning-line')
  }
  isSending.value = false
}
</script>

<template>
  <Header :title="$t('views.bot.title')" />

  <div class="flex flex-col items-center justify-center h-[calc(100%-64px)] p-6 text-center">
    <div class="mb-8">
      <i class="ri-robot-2-line text-8xl mb-4 block text-primary"></i>
      <h2 class="text-xl font-bold">{{ $t('views.bot.bot_name') }}</h2>
      <p class="text-sm max-w-xs mx-auto mt-2">
        {{ $t('views.bot.empty') }}
      </p>
    </div>

    <button
      class="btn btn-primary btn-lg gap-3 rounded-full px-8 shadow-lg transition-all active:scale-95"
      :disabled="isSending"
      @click="handleSend"
    >
      <span v-if="isSending" class="loading loading-spinner"></span>
      <i v-else class="ri-send-plane-2-line text-xl"></i>
      {{ $t('views.bot.send_now') }}
    </button>

    <p class="text-xs opacity-40 mt-6 max-w-4xl">
      {{ $t('views.bot.disclaimer') }}
    </p>
  </div>
</template>
