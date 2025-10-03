<script setup></script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center gap-3">
    <div class="flex flex-row items-center justify-center text-center gap-x-4">
      <h1 class="text-7xl font-bold text-error">{{ $t('views.not_found.title') }}</h1>
    </div>
    <p class="text-xl mt-4 text-base-content">{{ $t('views.not_found.content') }}</p>
    <p class="text-sm text-base-content opacity-70 mb-6">{{ $t('views.not_found.hint') }}</p>
    <button class="btn btn-primary" @click="$router.push('/')">
      {{ $t('views.not_found.button') }}
    </button>
  </div>
</template>
