<template>
  <button
    class="card bg-base-100 h-36 md:h-28 flex flex-col items-center justify-center gap-2.5 p-3 cursor-pointer hover:bg-base-200 active:scale-[0.97] transition-all duration-150 border border-base-300 rounded-2xl"
  >
    <div
      :class="['w-12 h-12 md:w-10 md:h-10 rounded-xl flex items-center justify-center', colorClass]"
    >
      <i :class="[icon, 'text-2xl md:text-xl']"></i>
    </div>
    <div class="text-center">
      <div class="font-semibold text-sm md:text-xs"><slot name="title"></slot></div>
      <div class="text-[11px] md:text-[10px] opacity-50 mt-0.5 leading-tight">
        <slot name="hint"></slot>
      </div>
    </div>
  </button>
</template>

<script setup>
defineProps(['icon', 'colorClass'])
</script>
