<script setup>
import { useRoute, useRouter } from 'vue-router'
import { cn } from '@/lib/utils'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const items = [
  { icon: 'ri-home-line', label: t("components.dock.home"), to: '/' },
  { icon: 'ri-settings-4-line', label: t("components.dock.settings"), to: '/settings' },
]

const isActive = (itemTo) => {
  if (itemTo === '/') {
    return route.path === '/'
  } else {
    return route.path.startsWith(itemTo)
  }
}
</script>

<template>
  <nav
    class="fixed bottom-0 left-0 right-0 z-50 pt-2 pb-2 flex justify-around border-t border-border backdrop-blur supports-[backdrop-filter]:bg-background/60"
    :style="{
      backgroundColor: 'rgba(0, 0, 0, 0.15)'
    }"
  >
    <button
      v-for="i in items"
      :key="i.to"
      @click="router.push(i.to)"
      class="flex flex-col items-center py-2 text-sm transition-colors hover:text-accent"
      :class="cn(isActive(i.to) ? 'text-accent' : 'text-muted-foreground')"
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
