<script setup lang="js">
</script>


<template>
  <div
    class="dock fixed bottom-0 left-0 w-full flex justify-around bg-base-200 py-1 border-t border-base-content/20 shadow-inner">

    <button class="flex flex-col items-center text-sm transition-colors"
      :class="{ 'text-primary dock-active': $route.name === 'Home', 'text-base-content hover:text-accent': $route.name !== 'Home' }"
      @click="$router.push('/')">
      <i class="ri-home-line text-xl"></i>
      <span class="dock-label">{{ $t("components.dock.home") }}</span>
    </button>

    <button class="flex flex-col items-center text-sm transition-colors"
      :class="{ 'text-primary dock-active': $route.name === 'Settings', 'text-base-content hover:text-accent': $route.name !== 'Settings' }"
      @click="$router.push('/settings')">
      <i class="ri-settings-4-line text-xl"></i>
      <span class="dock-label">{{ $t("components.dock.settings") }}</span>
    </button>

  </div>
</template>

<style scoped>
.dock {
  padding-bottom: env(safe-area-inset-bottom, 0);
}
</style>
