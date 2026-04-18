<script setup lang="ts">
defineProps<{
  header?: string | undefined,
  hint?: string | undefined,
}>()
</script>


<template>
  <div class="w-full gap-1 block">
    <span v-if="header" class="flex text-sm font-semibold">{{ $t(header)}}</span>
    <p v-if="hint" class="text-sm text-base-content/60">{{ $t(hint)}}</p>
    <ul tabindex="0" class="menu bg-base-100 rounded-box gap-2 w-full mt-2">
      <slot></slot>
    </ul>
  </div>
</template>

<style scoped>
</style>
