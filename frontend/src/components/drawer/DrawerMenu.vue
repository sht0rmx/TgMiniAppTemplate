<script setup>
import { authStatus, nav_items } from '@/main'
import { useUserStore } from '@/utils/stores/user'
import { computed } from 'vue'

const userStore = useUserStore()
const userData = computed(() => userStore.data)
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
    <div v-if="authStatus" class="flex flex-row p-2 items-center gap-3 is-drawer-close:flex-col">
      <div v-if="userData?.avatar_url" class="avatar placeholder flex-shrink-0">
        <div class="w-12 rounded-full">
          <img :src="userData.avatar_url" :alt="userData.name" />
        </div>
      </div>
      <div v-else class="avatar placeholder flex-shrink-0">
        <div class="w-12 rounded-full bg-accent text-accent-content">
          <span class="text-xl">{{ userData?.name?.charAt(0)?.toUpperCase() || 'U' }}</span>
        </div>
      </div>
      <div class="is-drawer-close:hidden is-drawer-close:mt-2 is-drawer-close:text-center min-w-0">
        <p class="font-semibold truncate">{{ userData?.name || 'User' }}</p>
        <p class="text-xs opacity-70 truncate">@{{ userData?.username || 'user' }}</p>
      </div>
    </div>
    <div
      v-else
      class="flex flex-col p-2 rounded-box is-drawer-close:rounded-full items-center bg-base-200/70 is-drawer-close:bg-base-100"
    >
      <div class="avatar placeholder">
        <div class="w-12 rounded-full bg-base-300 text-base-content is-drawer-close:w-10">
          <i class="ri-account-circle-2-line text-2xl"></i>
        </div>
      </div>
      <div class="text-center is-drawer-close:hidden mt-2">
        <p class="font-semibold">{{ $t('components.sidebar.auth.title') }}</p>
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
