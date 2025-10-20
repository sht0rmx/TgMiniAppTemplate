<script setup lang="js">
import { useRouter } from 'vue-router'
import SpinCode from "@/components/SpinCode.vue"

const router = useRouter()

function gotoSettings() {
  router.push('/settings')
}

const botName = import.meta.env.VITE_BOTNAME
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center gap-3 text-cbase w-md">
    <i class="ri-key-line text-8xl text-accent"></i>
    <h1 class="text-3xl font-bold">{{ $t('views.login.title') }}</h1>
    <SpinCode />
    <p class="text-hint text-sm max-w-xs text-center my-1">
      {{ $t('views.login.hint', { botname: botName }) }}
    </p>
  </div>
</template>
