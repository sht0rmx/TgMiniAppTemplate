<script setup lang="ts">
import { authStatus } from '@/main'
import { useUserStore } from '@/utils/stores/user'

const userStore = useUserStore()
</script>

<template>
  <div class="card bg-base-100 border border-base-300 shadow-sm overflow-hidden">
    <!-- Logged-in state -->
    <div v-if="authStatus && userStore.data" class="card-body p-4">
      <div class="flex items-center gap-4">
        <div class="avatar placeholder">
          <div
            class="w-14 h-14 rounded-full bg-linear-to-br from-primary to-secondary text-primary-content flex items-center justify-center"
          >
            <img
              v-if="userStore.data.avatar_url"
              :src="userStore.data.avatar_url"
              :alt="userStore.data.name"
              class="rounded-full object-cover"
              @error="userStore.data.avatar_url = null"
            />
            <span v-else class="text-xl font-bold uppercase">
              {{ userStore.data.name?.charAt(0) || 'U' }}
            </span>
          </div>
        </div>

        <div class="flex flex-col min-w-0">
          <span class="text-lg font-semibold truncate">
            {{ userStore.data.name }}
          </span>
          <div class="flex items-center gap-2">
            <span
              v-if="userStore.data.username"
              class="text-sm text-base-content/50 truncate"
            >
              @{{ userStore.data.username }}
            </span>
            <span
              class="badge badge-sm badge-soft badge-accent"
            >
              {{ userStore.data.role }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-else-if="authStatus" class="card-body p-5">
      <div class="flex items-center gap-3 text-base-content/60">
        <span class="loading loading-spinner loading-sm"></span>
        <span>{{ $t('badges.load') }}</span>
      </div>
    </div>

    <!-- Not logged-in state -->
    <div v-else class="card-body p-5">
      <div class="flex items-center gap-4">
        <div class="avatar placeholder">
          <div
            class="w-14 h-14 rounded-full bg-base-200 flex items-center justify-center"
          >
            <i class="ri-user-line text-2xl text-base-content/40" />
          </div>
        </div>

        <div class="flex flex-col flex-1 min-w-0">
          <p class="font-semibold">
            {{ $t('components.sidebar.auth.title') }}
          </p>
          <p class="text-sm text-base-content/50">
            {{ $t('components.sidebar.auth.hint') }}
          </p>
        </div>
      </div>

      <button
        class="btn btn-primary btn-sm mt-3 w-full"
        @click="
          $router.push({
            path: '/login',
            query: { redirect: $router.currentRoute.value.path },
          })
        "
      >
        <i class="ri-login-box-line" />
        {{ $t('components.sidebar.auth.btn') }}
      </button>
    </div>
  </div>
</template>
