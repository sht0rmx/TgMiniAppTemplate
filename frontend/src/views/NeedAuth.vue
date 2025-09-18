<script lang="js">
const tgUrl = import.meta.env.VITE_TG_MINIAPP_START
</script>


<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center gap-3">
    <i class="ri-error-warning-line text-6xl text-warning"></i>
    <h1 class="text-3xl font-bold">{{ $t('views.need_auth.title') }}</h1>
    <p class="text-gray-500">{{ $t('views.need_auth.hint') }}</p>
    <a class="btn btn-soft btn-accent px-8" :href="tgUrl" target="_blank">
      {{ $t('views.need_auth.button') }}
    </a>
  </div>
</template>