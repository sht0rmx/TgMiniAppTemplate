<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  src: string
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Audio Player',
})

const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const error = ref<string>('')

const formattedCurrentTime = computed(() => formatTime(currentTime.value))
const formattedDuration = computed(() => formatTime(duration.value))
const progressPercentage = computed(() => (currentTime.value / duration.value) * 100 || 0)

function formatTime(seconds: number): string {
  if (!isFinite(seconds) || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function togglePlay() {
  if (!audioRef.value) return

  try {
    if (isPlaying.value) {
      audioRef.value.pause()
      isPlaying.value = false
    } else {
      await audioRef.value.play()
      isPlaying.value = true
    }
  } catch (err: any) {
    error.value = `Playback error: ${err.message}`
    isPlaying.value = false
  }
}

function onTimeUpdate() {
  if (!audioRef.value) return
  currentTime.value = audioRef.value.currentTime
}

function onLoadedMetadata() {
  if (!audioRef.value) return
  duration.value = audioRef.value.duration
  error.value = ''
}

function onEnded() {
  isPlaying.value = false
  if (audioRef.value) {
    audioRef.value.currentTime = 0
  }
}

function onError() {
  if (!audioRef.value) return
  const errorMap: Record<number, string> = {
    1: 'Loading aborted',
    2: 'Network error',
    3: 'Decoding failed',
    4: 'Audio format not supported',
  }
  error.value = errorMap[audioRef.value.error?.code || 4] || 'Unknown error'
  isPlaying.value = false
}

function setCurrentTime(evt: Event) {
  const target = evt.target as HTMLInputElement
  const time = parseFloat(target.value)
  if (audioRef.value) {
    audioRef.value.currentTime = time
    currentTime.value = time
  }
}

function setVolume(evt: Event) {
  const target = evt.target as HTMLInputElement
  const val = parseFloat(target.value)
  volume.value = val
  if (audioRef.value) {
    audioRef.value.volume = val
  }
}
</script>

<template>
  <div class="w-full bg-base-200 rounded-xl p-4 space-y-3">
    <audio
      ref="audioRef"
      :src="src"
      preload="metadata"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @ended="onEnded"
      @error="onError"
    ></audio>

    <!-- Title -->
    <div class="text-sm font-medium truncate">{{ title }}</div>

    <!-- Error Message -->
    <div v-if="error" class="alert alert-error">
      <i class="ri-error-warning-line"></i>
      <span class="text-sm">{{ error }}</span>
    </div>

    <!-- Progress bar -->
    <div class="flex items-center gap-2">
      <span class="text-xs opacity-60 min-w-fit">{{ formattedCurrentTime }}</span>
      <input
        type="range"
        min="0"
        :max="duration || 0"
        :value="currentTime"
        class="range range-sm range-primary flex-1"
        @input="setCurrentTime"
      />
      <span class="text-xs opacity-60 min-w-fit">{{ formattedDuration }}</span>
    </div>

    <!-- Controls -->
    <div class="flex items-center gap-3">
      <!-- Play/Pause -->
      <button class="btn btn-circle btn-primary btn-sm" @click="togglePlay" :disabled="!!error">
        <i :class="isPlaying ? 'ri-pause-fill' : 'ri-play-fill'" class="text-lg"></i>
      </button>

      <!-- Volume -->
      <div class="flex items-center gap-2 flex-1">
        <i class="ri-volume-down-line text-sm opacity-60"></i>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          :value="volume"
          class="range range-xs flex-1"
          @input="setVolume"
        />
        <i class="ri-volume-up-line text-sm opacity-60"></i>
      </div>
    </div>
  </div>
</template>
