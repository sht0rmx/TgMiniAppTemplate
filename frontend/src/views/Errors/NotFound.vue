<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
</script>

<template>
  <ErrorPage
    :code="$t('views.not_found.code.404.title')"
    :desc="$t('views.not_found.code.404.content')"
    :hint="$t('views.not_found.code.404.hint')"/>
</template>
