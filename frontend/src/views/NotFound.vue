<script setup>
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen text-center gap-3">
    <i class="ri-error-warning-line text-6xl text-warning"></i>
    <h1 class="text-7xl font-bold text-error">404</h1>
    <p class="text-xl mt-4 text-base-content">Oops! Page not found.</p>
    <p class="text-sm text-base-content opacity-70 mb-6">The page you are looking for does not exist.</p>
    <button class="btn btn-primary" @click="$router.push('/')">
      Go Home
    </button>
  </div>
</template>