<script lang="js">
const tgUrl = import.meta.env.VITE_TG_MINIAPP_START
</script>


<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center gap-3">
    <i class="ri-error-warning-line text-6xl text-warning"></i>
    <h1 class="text-3xl font-bold">Not in Telegram</h1>
    <p class="text-gray-500">Please open this app inside Telegram Mini App</p>
    <a class="btn btn-soft btn-accent px-8" :href="tgUrl" target="_blank">AniParseBot</a>
  </div>
</template>