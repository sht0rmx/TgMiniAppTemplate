<template>
  <div class="card flex items-center justify-center p-10 bg-white rounded-xl shadow w-50 h-50">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import QRCode from 'qrcode'

const props = defineProps({
  url: { type: String, required: true },
  size: { type: Number, default: 192 },
})

const canvas = ref<HTMLCanvasElement | null>(null)

async function draw(val: string) {
  if (!val || !canvas.value) return

  canvas.value.width = props.size
  canvas.value.height = props.size

  const ctx = canvas.value.getContext('2d')
  if (ctx) ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)

  try {
    await QRCode.toCanvas(canvas.value, val.trim(), {
      width: props.size,
      margin: 1,
      color: { dark: '#000', light: '#fff' },
    })
  } catch (err) {
    console.error('Failed to draw QR:', err)
  }
}

onMounted(() => nextTick(() => draw(props.url)))
watch(
  () => props.url,
  (v) => nextTick(() => draw(v)),
)
</script>
