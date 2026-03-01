<script setup lang="ts">
defineProps<{
  text: string
  icon: string
}>()
</script>

<template>
  <li class="rounded-lg">
    <button class="w-full flex items-center gap-3">
      <div class="flex w-full items-center">
        <slot name="content">
          <div class="flex items-center gap-2">
            <i class="text-xl" :class="icon"></i>
            <span>{{ $t(text) }}</span>
          </div>
        </slot>

        <div class="flex-1 flex justify-end">
          <slot />
        </div>
      </div>
    </button>
  </li>
</template>
