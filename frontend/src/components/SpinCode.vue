<script setup lang="ts">
import { ref, onMounted } from "vue"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

const code = ref<string[]>(["-", "-", "-", "-", "-", "-"])
const spinning = ref(false)

function genCode() {
  return Array.from({ length: 6 }, () => Math.floor(Math.random() * 10).toString())
}

function spin() {
  spinning.value = true
  const newCode = genCode()
  newCode.forEach((num, i) => {
    setTimeout(() => {
      code.value[i] = num
      if (i === newCode.length - 1) spinning.value = false
    }, 200 * i)
  })
}

onMounted(() => spin())
</script>

<template>
    <div class="flex space-x-2 mt-3 text-card-foreground">
      <div
        v-for="(n, i) in code"
        :key="i"
        class="w-10 h-14 flex items-center justify-center bg-muted text-2xl font-bold rounded-md shadow-inner animate-in fade-in zoom-in duration-500"
        :style="{ transitionDelay: `${i * 100}ms` }"
      >
        {{ n }}
      </div>
    </div>
</template>

<style scoped>
@keyframes spinNum {
  0% { transform: translateY(100%); opacity: 0; }
  50% { transform: translateY(-20%); opacity: 1; }
  100% { transform: translateY(0); }
}

.animate-in {
  animation: spinNum 0.4s ease-out;
}
</style>
