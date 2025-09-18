<template>
  <div :class="['flex flex-col min-h-screen bg-base-200', { 'pb-14': $route.name != 'NeedAuth' }]">

    <main :class="['flex-1 text-sm text-base-content flex justify-center', { 'p-4': $route.name != 'NeedAuth' }]">
      <div :class="[
        'w-full',
        $route.name === 'NeedAuth' ? 'max-w-sm' : 'max-w-2xl'
      ]">
        <router-view />
      </div>
    </main>

    <BottomDock v-if="$route.name != 'NeedAuth'" />
  </div>
</template>

<script setup>
import BottomDock from '@/components/BottomDock.vue'
</script>
