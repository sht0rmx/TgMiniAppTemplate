<script setup lang="js">
import { Button } from '@/components/ui/button/index.js'

defineProps({
  code: String,
  desc: String,
  hint: String,
})
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center gap-3 text-cbase">
    <div class="flex flex-row items-center justify-center text-center gap-x-4">
      <h1 class="text-7xl font-bold text-destructive">{{ code }}</h1>
    </div>
    <p class="text-xl mt-4 text-base-content">{{ desc }}</p>
    <p class="text-sm text-base-content opacity-70 mb-6">{{ hint }}</p>
    <Button class="flex-row btn btn-primary text-center" @click="$router.back()">
      <i class="ri-arrow-left-line"/>
      {{ $t('views.not_found.back_button') }}
    </Button>
  </div>
</template>
