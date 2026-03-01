<script setup lang="js"></script>

<template>
  <div class="lg:h-full flex flex-col items-center justify-center space-y-3">
    <i class="ri-drop-line text-accent text-8xl"></i>
    <h1 class="font-bold text-3xl">{{ $t('views.home.title') }}</h1>
    <p class="text-center max-w-lg opacity-70">
      {{ $t('views.home.description') }}
    </p>
    <button class="btn btn-primary" @click="$router.push('/menu/settings')">
      {{ $t('views.home.button') }}
    </button>
    <p class="text-sm opacity-30 max-w-xs text-center my-1">
      {{ $t('views.home.hint') }}
    </p>
  </div>
</template>
