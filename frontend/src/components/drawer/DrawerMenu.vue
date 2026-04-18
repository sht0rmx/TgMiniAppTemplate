<script setup>
import { authStatus, nav_items, drawerOpen } from '@/main'
import { useUserStore } from '@/utils/stores/user'
import { computed } from 'vue'

const userStore = useUserStore()
const userData = computed(() => userStore.data)
</script>

<template>
  <div
    class="menu min-h-full p-2 justify-between is-drawer-close:w-22 is-drawer-open:w-60 group overflow-hidden flex flex-col"
  >
    <div class="mt-3">
      <div class="flex flex-col gap-1 mb-2 ml-2">
        <div
          class="flex flex-row items-center justify-between is-drawer-close:justify-center is-drawer-close:mb-5"
        >
          <div class="flex items-center min-w-0">
            <i class="ri-box-3-line text-5xl text-accent leading-none shrink-0" />
            <span class="font-bold text-3xl is-drawer-close:hidden truncate ml-2">
              {{ $t('components.sidebar.title') }}
            </span>
          </div>

          <label
            for="sidebar"
            class="swap swap-rotate max-w-4 max-h-8 btn btn-square btn-ghost opacity-0 group-hover:opacity-100 transition-opacity duration-200"
            :class="{ 'swap-active': !drawerOpen }"
          >
            <i class="swap-on ri-arrow-right-wide-line" />
            <i class="swap-off ri-arrow-left-wide-line" />
          </label>
        </div>
        <p
          class="text-xs ml-2 mr-2 is-drawer-close:hidden wrap-break-word overflow-hidden text-ellipsis"
        >
          {{ $t('components.sidebar.hint') }}
        </p>
      </div>

      <ul class="mx-0 is-drawer-open:mx-4 p-0">
        <li
          v-for="i in nav_items"
          :key="i.to"
          @click="$router.push(i.to)"
          class="flex justify-center"
          :class="[{ 'text-primary': $route.path === i.to }]"
        >
          <button
            class="w-full p-2 is-drawer-close:tooltip is-drawer-close:tooltip-right items-center flex gap-4 is-drawer-close:justify-center"
            :data-tip="$t(i.label)"
          >
            <i :class="[i.icon, 'text-2xl shrink-0', { 'opacity-70': $route.path !== i.to }]"></i>
            <span
              class="is-drawer-close:hidden truncate whitespace-nowrap"
              :class="{ 'opacity-70': $route.path !== i.to }"
            >
              {{ $t(i.label) }}
            </span>
          </button>
        </li>
      </ul>
    </div>

    <div class="w-full overflow-hidden">
      <div
        v-if="authStatus"
        class="flex flex-row p-3 items-center gap-3 is-drawer-close:flex-col is-drawer-close:justify-center hover:bg-base-200 rounded-full transition-all duration-150"
        @click="$router.push('/menu/settings')"
      >
        <div class="avatar placeholder shrink-0">
          <div class="w-12 rounded-full ring ring-base-300 ring-offset-base-100 ring-offset-2">
            <img v-if="userData?.avatar_url" :src="userData.avatar_url" :alt="userData.name" />
            <div
              v-else
              class="bg-accent text-accent-content w-full h-full flex items-center justify-center"
            >
              <span class="text-xl">{{ userData?.name?.charAt(0)?.toUpperCase() || 'U' }}</span>
            </div>
          </div>
        </div>

        <div class="is-drawer-close:hidden min-w-0 flex-1">
          <p class="font-semibold truncate">{{ userData?.name || 'User' }}</p>
          <p class="text-xs opacity-70 truncate">@{{ userData?.username || 'user' }}</p>
        </div>
      </div>

      <div
        v-else
        class="flex flex-col p-2 rounded-box is-drawer-close:rounded-full items-center bg-base-200/70 is-drawer-close:bg-transparent overflow-hidden"
      >
        <div class="avatar placeholder shrink-0">
          <div
            class="w-12 rounded-full bg-base-300 text-base-content is-drawer-close:w-10 flex items-center justify-center"
          >
            <i class="ri-account-circle-2-line text-2xl"></i>
          </div>
        </div>
        <div class="text-center is-drawer-close:hidden mt-2 w-full">
          <p class="font-semibold truncate px-1">{{ $t('components.sidebar.auth.title') }}</p>
          <p class="text-xs opacity-70 truncate px-1">{{ $t('components.sidebar.auth.hint') }}</p>
          <button
            class="btn btn-soft btn-warning btn-sm w-full mt-2"
            @click="$router.push('/login')"
          >
            {{ $t('components.sidebar.auth.btn') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
