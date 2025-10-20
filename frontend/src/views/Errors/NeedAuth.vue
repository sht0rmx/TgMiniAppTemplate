<script setup>
import { Button } from '@/components/ui/button'

const tgUrl = import.meta.env.VITE_TG_MINIAPP_START
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center gap-3 text-cbase">
    <div class="flex flex-row items-center justify-center text-center gap-x-4">
      <i class="text-7xl font-bold ri-chat-1-line"></i>
    </div>
    <h1 class="text-3xl font-bold">{{ $t('views.need_auth.title') }}</h1>
    <p class="text-sm text-base-content opacity-70 mb-6">{{ $t('views.need_auth.hint') }}</p>
    <div class="flex flex-row gap-3">
      <Button as="a" :href="tgUrl" target="_blank" class="font-semibold text-white
           bg-blue-500 border border-blue-300 hover:bg-blue-600 hover:shadow-md">
        {{ $t('views.need_auth.button') }}
      </Button>

      <Button @click="$router.push('/login')" class="font-semibold text-gray-800
           bg-gray-100 border border-gray-300 hover:bg-gray-200 hover:shadow-md">
        {{ $t('views.need_auth.login_code') }}
      </Button>
    </div>
  </div>
</template>
