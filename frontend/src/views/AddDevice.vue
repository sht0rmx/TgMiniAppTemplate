<script setup lang="ts">
import { ref } from 'vue'
import { PinInput, PinInputGroup, PinInputSlot } from '@/components/ui/pin-input'

const value = ref<string[]>([])
const handleComplete = (e: string[]) => {
  console.log(value)
}

const emit = defineEmits(['close'])
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
    @click.self="emit('close')"
  >
    <div class="w-full max-w-md bg-card rounded-2xl shadow-xl p-6 animate-slideUp mx-4">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">{{ $t('views.addDevice.title') }}</h2>
      </div>
      <div class="flex flex-col justify-center items-center gap-3">
        <PinInput id="pin-input" v-model="value" placeholder="○" @complete="handleComplete">
          <PinInputGroup class="flex">
            <PinInputSlot
              v-for="(_, idx) in 6"
              :key="idx"
              :index="idx"
              class="w-12 h-14 text-2xl font-bold bg-card text-card-foreground flex items-center justify-center focus:ring-0 focus:outline-none"
              :class="{
                'border-t border-b border-border': true,
                'border-r border-border': idx === 5,
              }"
            />
          </PinInputGroup>
        </PinInput>
        <p class="text-hint text-sm max-w-xs text-center my-1">
          {{ $t('views.addDevice.hint') }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0%);
    opacity: 1;
  }
}

.animate-slideUp {
  animation: slideUp 0.35s ease;
}
</style>
