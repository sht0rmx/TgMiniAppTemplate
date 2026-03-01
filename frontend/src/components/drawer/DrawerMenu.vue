<script setup>
import { authStatus, nav_items } from '@/main'
</script>

<template>
  <div class="menu min-h-full p-2 justify-between is-drawer-close:w-22 is-drawer-open:w-60 group">
    <div class="mt-3">
      <div class="flex flex-col gap-1 mb-2 ml-2">
        <div class="flex flex-row items-center justify-between is-drawer-close:mb-5">
          <div class="flex items-center">
            <i class="ri-box-3-line text-5xl text-accent leading-none" />
            <span class="font-bold text-3xl is-drawer-close:hidden">{{
              $t('components.sidebar.title')
            }}</span>
          </div>
          <label
            for="sidebar"
            aria-label="close drawer"
            class="swap swap-rotate max-w-4 max-h-8 btn btn-square btn-ghost opacity-0 group-hover:opacity-100 transition-opacity duration-200 is-drawer-close:tooltip is-drawer-close:tooltip-right is-drawer-close:swap-active"
            :data-tip="$t('components.sidebar.expand_hint')"
          >
            <i class="swap-on ri-arrow-right-wide-line" />
            <i class="swap-off ri-arrow-left-wide-line" />
          </label>
        </div>
        <p class="text-xs ml-2 is-drawer-close:hidden whitespace-nowrap">
          {{ $t('components.sidebar.hint') }}
        </p>
      </div>
      <ul class="mx-4">
        <li
          v-for="i in nav_items"
          :key="i.to"
          @click="$router.push(i.to)"
          :class="[{ 'text-primary': $route.path === i.to }]"
        >
          <button
            class="w-full p-2 is-drawer-close:tooltip is-drawer-close:tooltip-right is-drawer-close:pb-0.1 items-center"
            :data-tip="$t(i.label)"
          >
            <i :class="[i.icon, 'text-2xl', { 'opacity-70': $route.path !== i.to }]"></i>
            <span class="is-drawer-close:hidden" :class="{ 'opacity-70': $route.path !== i.to }">{{
              $t(i.label)
            }}</span>
          </button>
        </li>
      </ul>
    </div>
    <div v-if:="authStatus"></div>
    <div
      v-else
      class="flex flex-col p-2 rounded-box is-drawer-close:rounded-full items-center bg-base-200/70 is-drawer-close:bg-base-100"
    >
      <i class="ri-account-circle-2-line text-5xl text-accent leading-none" />
      <div class="text-center is-drawer-close:hidden">
        <p>{{ $t('components.sidebar.auth.title') }}</p>
        <p class="text-xs opacity-70">{{ $t('components.sidebar.auth.hint') }}</p>
      </div>
      <button
        class="btn btn-soft btn-warning w-full mt-2 is-drawer-close:hidden"
        @click="$router.push('/login')"
      >
        {{ $t('components.sidebar.auth.btn') }}
      </button>
    </div>
  </div>
</template>
