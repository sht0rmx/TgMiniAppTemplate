<script setup>
import { Card } from '@/components/ui/card'

const props = defineProps({
  title: { type: String, required: false }
})
</script>

<template>
  <section class="space-y-1">
    <h2 v-if="title" class="text-sm font-semibold tracking-wide text-muted-foreground">
      {{ title }}
    </h2>

    <Card class="shadow-sm border rounded-2xl">
      <div class="divide-y flex flex-col">
        <slot />
      </div>
    </Card>
  </section>
</template>
