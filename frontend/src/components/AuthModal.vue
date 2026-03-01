<script setup lang="ts">
import { lockPage } from '@/main.ts'
</script>

<template>
  <div class="modal" :class="{ 'modal-open': lockPage }" role="dialog">
    <div class="modal-box w-3/4 max-w-sm">
      <h3 class="text-lg font-bold">{{ $t('views.auth.locked_title') }}</h3>
      <p class="py-4">{{ $t('views.auth.locked_description') }}</p>
      <div class="flex flex-row w-full items-center gap-3">
        <button class="btn btn-soft btn-primary flex-1" @click="$router.push('/login')">
          <span class="ri-login-box-line"></span>
          {{ $t('views.auth.login_button') }}
        </button>
        <button class="btn btn-soft flex-1" @click="$router.back()">
          {{ $t('views.auth.back_button') }}
        </button>
      </div>
    </div>
  </div>
</template>
