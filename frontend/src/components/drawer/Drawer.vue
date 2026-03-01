<script setup lang="ts">
import DrawerMenu from '@/components/drawer/DrawerMenu.vue'
import { hiddenNav, isLoading } from '@/main'
</script>

<template>
  <div class="drawer" :class="{ 'md:drawer-open': !hiddenNav }">
    <input id="sidebar" type="checkbox" class="drawer-toggle" />

    <div class="drawer-content">
      <slot />
    </div>

    <div v-show="!hiddenNav && !isLoading" class="drawer-side overflow-visible">
      <label for="sidebar" class="drawer-overlay"></label>
      <DrawerMenu />
    </div>
  </div>
</template>
