<script>
import { ref } from 'vue';

const show = ref(false);
let updateSWCallback = null;

function update() {
  if (updateSWCallback) updateSWCallback();
  show.value = false;
}

function close() {
  show.value = false;
}

export function notifyUpdate(updateSW) {
  updateSWCallback = updateSW;
  show.value = true;
}

export default {
  setup() {
    return { show, update, close };
  }
}
</script>

<template>
  <div v-if="show" class="fixed bottom-4 right-4 z-50">
    <div role="alert" class="alert alert-info shadow-lg flex items-center gap-4">
      <i class="ri-refresh-line text-2xl"></i>
      <div class="flex-1">
        <span>{{ $t("components.popup.text") }}</span>
      </div>
      <div class="flex-none flex gap-2">
        <button class="btn btn-sm btn-primary" @click="update">{{ $t("components.popup.update") }}</button>
        <button class="btn btn-sm btn-ghost" @click="close">{{ $t("components.popup.close") }}</button>
      </div>
    </div>
  </div>
</template>
