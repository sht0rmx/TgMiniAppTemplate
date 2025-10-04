<script setup lang="js">
import { useRouter } from 'vue-router'

const router = useRouter()

function gotoSettings() {
  router.push('/settings')
}
</script>

<template>
  <div class="flex flex-col items-center justify-center space-y-3 mt-8">
    <i class="ri-drop-line text-8xl text-accent"></i>
    <h1 class="text-3xl font-bold">{{ $t('views.home.title') }}</h1>
    <p class="text-gray-400 text-base max-w-lg text-center">
      {{ $t('views.home.description') }}
    </p>
    <button class="btn btn-soft btn-accent px-8 mt-6" @click="gotoSettings()">
      {{ $t('views.home.button') }}
    </button>
    <p class="text-gray-600 text-sm max-w-xs text-center my-1">
      {{ $t('views.home.hint') }}
    </p>
  </div>
</template>
