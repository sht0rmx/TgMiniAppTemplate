<script setup>
import { useRoute, useRouter } from 'vue-router'
import { cn } from '@/lib/utils'

const route = useRoute()
const router = useRouter()

const items = [
  { icon: 'ri-home-line', label: 'Home', to: '/' },
  { icon: 'ri-settings-4-line', label: 'Settings', to: '/settings' }
]
</script>

<template>
  <nav
    class="fixed bottom-0 left-0 right-0 z-50 flex justify-around border-t border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    :style="{ paddingBottom: 'var(--tg-safe-area-inset-bottom, 0px)' }"
  >
    <button
      v-for="i in items"
      :key="i.to"
      @click="router.push(i.to)"
      class="flex flex-col items-center py-2 text-sm transition-colors hover:text-accent"
      :class="cn(
        route.path === i.to
          ? 'text-primary'
          : 'text-muted-foreground'
      )"
    >
      <i :class="[i.icon, 'text-xl leading-none']"></i>
      <span class="text-xs mt-0.5">{{ i.label }}</span>
    </button>
  </nav>
</template>


<style scoped>
nav {
  bottom: var(--tg-safe-area-inset-bottom, 0px);
}
nav::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: calc(0px - var(--tg-safe-area-inset-bottom, 0px));
  height: var(--tg-safe-area-inset-bottom, 0px);
  background-color: inherit;
}
</style>
