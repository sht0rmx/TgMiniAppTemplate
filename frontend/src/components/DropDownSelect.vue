<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="btn m-1 flex items-center gap-2">
      <span>{{ labelFn ? labelFn(modelValue) : modelValue }}</span>
      <i class="ri-arrow-down-s-line leading-none"></i>
    </div>

    <ul
      tabindex="0"
      class="dropdown-content menu bg-base-300 rounded-box z-1 w-max min-w-[6rem] p-2 shadow-xl"
    >
      <li v-for="item in items" :key="item">
        <button
          class="w-full text-left"
          :class="item === modelValue ? 'bg-accent text-gray-900 pointer-events-none' : ''"
          @click="$emit('update:modelValue', item)"
        >
          {{ labelFn ? labelFn(item) : item }}
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  items: Array,
  modelValue: [String, Number],
  labelFn: Function
})
defineEmits(['update:modelValue'])
</script>
