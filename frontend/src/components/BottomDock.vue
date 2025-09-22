<script setup>
</script>

<template>
  <div
    class="dock dock-md dock-safe">

    <button class="flex flex-col items-center text-sm transition-colors"
      :class="{ 'text-primary dock-active': $route.name === 'Home', 'text-base-content hover:text-accent': $route.name !== 'Home' }"
      @click="$router.push('/')">
      <i class="ri-home-line text-xl leading-none"></i>
      <span class="dock-label">{{ $t("components.dock.home") }}</span>
    </button>

    <button class="flex flex-col items-center text-sm transition-colors"
      :class="{ 'text-primary dock-active': $route.name === 'Settings', 'text-base-content hover:text-accent': $route.name !== 'Settings' }"
      @click="$router.push('/settings')">
      <i class="ri-settings-4-line text-xl leading-none"></i>
      <span class="dock-label">{{ $t("components.dock.settings") }}</span>
    </button>
    
  </div>
</template>

<style scoped>
.dock-safe{
  bottom: var(--tg-safe-area-inset-bottom, 0px);
}
.dock::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: calc(0px - var(--tg-safe-area-inset-bottom, 0px));
  height: var(--tg-safe-area-inset-bottom, 0px);
  background-color: inherit;
}
</style>
