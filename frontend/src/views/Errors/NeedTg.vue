<script setup>
import { Button } from '@/components/ui/button'

const tgUrl = import.meta.env.VITE_TG_MINIAPP_START
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center gap-3 max-w-sm">
    <i class="ri-error-warning-line text-6xl text-warning"></i>
    <h1 class="text-3xl font-bold">{{ $t('views.need_auth.title') }}</h1>
    <p class="text-gray-500">{{ $t('views.need_auth.hint') }}</p>
    <Button class="px-8">
      <a :href="tgUrl" target="_blank">
        {{ $t('views.need_auth.button') }}
      </a>
    </Button>
  </div>
</template>
