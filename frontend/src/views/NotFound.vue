<template>
  <div class="h-full flex items-center justify-center">
    <div class="flex flex-col items-center justify-center text-center gap-3">
      <h1 class="text-7xl font-bold text-error">404</h1>
      <div class="mb-3">
        <p class="text-xl">{{ $t('views.not_found.content') }}</p>
        <p class="text-sm opacity-70">{{ $t('views.not_found.hint') }}</p>
      </div>
      <button class="btn btn-soft btn-primary" @click="$router.push('/')">
        <i class="ri-arrow-left-line" />
        {{ $t('views.not_found.back_button') }}
      </button>
    </div>
  </div>
</template>