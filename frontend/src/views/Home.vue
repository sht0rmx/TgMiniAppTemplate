<script setup lang="js">
import { useRouter } from 'vue-router';

const router = useRouter()

function gotoSettings() {
  router.push('/settings')
}

</script>

<template>
  <div class="flex flex-col items-center justify-center space-y-3 mt-8 mb-12"> <i
      class="ri-drop-line text-8xl text-accent"></i>
    <h1 class="text-3xl font-bold">TG MiniApp Example</h1>
    <p class="text-gray-400 text-base max-w-lg text-center">
      Its simple repo that may be used as start point for your project.
      Template uses VueJs as base js framework, also here is a ui lib and simple icon pack,
      for simpler usage experience this template we choose PocketBase as go backend framework.
      Lib for communicate with TelegramApi: PyTelegramBotApi
    </p>
    <p class="text-gray-200 text-base max-w-sm text-center my-6">
      For check status of api we may open setting tab by button on dock or click on the button
    </p>
    <button class="btn btn-soft btn-accent px-8" @click="gotoSettings()">Open settings</button>
  </div>
</template>
