<script setup>
import { Card } from '@/components/ui/card'

const props = defineProps({
  title: { type: String, required: false }
})
</script>

<template>
  <section class="space-y-1">
    <h2 v-if="title" class="text-sm tracking-wide text-section-header uppercase">
      {{ title }}
    </h2>

    <Card class="rounded-2xl">
      <div class="divide-y flex flex-col text-cbase">
        <slot />
      </div>
    </Card>
  </section>
</template>
