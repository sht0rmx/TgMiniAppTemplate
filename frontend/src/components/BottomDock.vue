<script setup>
import { nav_items } from '@/main'
</script>

<template>
  <div class="dock dock-sm md:hidden" id="navbar">
    <button
      v-for="i in nav_items"
      :key="i.to"
      @click="$router.push(i.to)"
      :class="{
        'dock-active text-primary':
          i.to !== '/' ? $route.path.includes(i.to) : $route.path === i.to,
      }"
    >
      <i :class="[i.icon, 'text-xl leading-none']"></i>
      <span class="dock-label">{{ $t(i.label) }}</span>
    </button>
  </div>
</template>

<style scoped>
#navbar {
  bottom: calc(3px + var(--tg-safe-area-inset-bottom, 0px));
}

#navbar::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: calc(-3px - var(--tg-safe-area-inset-bottom, 0px));
  height: calc(3px + var(--tg-safe-area-inset-bottom, 0px));
  background-color: inherit;
}
</style>
