<script setup lang="ts">
import Header from '@/components/Header.vue'
const menuItems = [
  {
    path: '/menu/files',
    icon: 'ri-folder-3-line',
    colorClass: 'bg-accent/10 text-accent',
    title: 'views.menu.files',
    hint: 'views.menu.files_hint',
  },
  {
    path: '/menu/bot',
    icon: 'ri-robot-2-line',
    colorClass: 'bg-primary/10 text-primary',
    title: 'views.menu.bot',
    hint: 'views.menu.bot_hint',
  },
  {
    path: '/components',
    icon: 'ri-palette-line',
    colorClass: 'bg-warning/10 text-warning',
    title: 'views.menu.components',
    hint: 'views.menu.components_hint',
    isComponent: true,
  },
]
</script>

<template>
  <div class="flex flex-col min-h-full">
    <Header :title="$t('views.menu.title')" :settings_show="true">
      <button
        @click="$router.push('/menu/settings')"
        class="tooltip tooltip-left"
        :data-tip="$t('views.menu.settings_tooltip')"
      >
        <i class="ri-settings-3-line text-2xl md:text-3xl leading-none" />
      </button>
    </Header>

    <div class="grid grid-cols-2 gap-4 max-w-xl mx-auto">
      <button
        v-for="item in menuItems"
        :key="item.title"
        class="card bg-base-100 h-36 md:h-28 flex flex-col items-center justify-center gap-2.5 p-3 cursor-pointer hover:bg-base-200 active:scale-[0.97] transition-all duration-150 border border-base-300 rounded-2xl"
        @click="$router.push(item.path)"
      >
        <div
          :class="[
            'w-12 h-12 md:w-10 md:h-10 rounded-xl flex items-center justify-center',
            item.colorClass,
          ]"
        >
          <i :class="[item.icon, 'text-2xl md:text-xl']"></i>
        </div>

        <div class="text-center">
          <div class="font-semibold text-sm md:text-xs">
            {{ $t(item.title) }}
          </div>
          <div class="text-[11px] md:text-[10px] opacity-50 mt-0.5 leading-tight">
            {{ $t(item.hint) }}
          </div>
        </div>
      </button>
    </div>
  </div>
</template>
