<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { backButton, isTgEnv } from '@/main'

defineProps({
  title: String,
})
</script>

<template>
  <div>
    <div
      ref="headerRef"
      class="fixed flex flex-row top-0 left-0 right-0 z-50 header-box bg-base-300/60 backdrop-blur-md transition-all duration-300"
    >
      <div class="flex flex-row items-center justify-between w-full gap-3 px-4 py-2 md:pt-6 md:pl-6">
        <div v-if="backButton" class="hidden md:flex items-center">
          <button @click="$router.back()" class="hover:opacity-70">
            <i class="ri-arrow-left-line text-2xl" />
          </button>
        </div>

        <slot name="content">
          <h1 class="text-2xl font-semibold flex-1 md:text-left md:text-4xl" :class="{'text-center' : isTgEnv}">
            {{ title }}
          </h1>
        </slot>

        <div v-if="!isTgEnv">
          <slot />
        </div>
      </div>
    </div>

    <div class="mb-10 md:mb-15" :class="{'mb-12': isTgEnv}"/>
  </div>
</template>

<style scoped>
.header-box {
  padding-top: calc(var(--tg-safe-area-inset-top, 0px));
  overflow-x: clip;
}
</style>

<style>
@media (min-width: 768px) {
  /* sidebar collapsed (checkbox unchecked) */
  .drawer.md\:drawer-open > .drawer-content .header-box {
    left: 5.5rem;
  }
  /* sidebar expanded (checkbox checked) */
  .drawer.md\:drawer-open:has(> .drawer-toggle:checked) > .drawer-content .header-box {
    left: 15rem;
  }
}
</style>
