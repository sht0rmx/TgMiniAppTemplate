<script setup lang="ts">
import Header from '@/components/Header.vue'
import Card from '@/components/menu/Card.vue'
import Menu from '@/components/menu/Menu.vue'
import { showPush } from '@/utils/alert'
import { ref, computed, defineComponent, h } from 'vue'

type ComponentKey =
  | 'header'
  | 'menu'
  | 'alert'
  | 'alerts'
  | 'badges'
  | 'modals'
  | 'inputs'

interface ComponentDef {
  name: string
  code: string
}

const selected = ref<ComponentKey>('header')

/* ---------------- PREVIEWS ---------------- */

const HeaderPreview = defineComponent({
  setup() {
    return () =>
      h('div', { class: 'w-full' }, [
        h(Header, { title: 'Page Title', settings_show: true }),
        h('div', { class: 'p-4 text-sm' }, 'Header preview'),
      ])
  },
})

const MenuPreview = defineComponent({
  setup() {
    return () =>
      h(Menu, { header: 'Section' }, () => [
        h(Card, {}, {
          content: () =>
            h('div', { class: 'flex justify-between w-full' }, [
              h('span', 'Item 1'),
              h('i', { class: 'ri-arrow-right-line' }),
            ]),
        }),
        h(Card, {}, {
          content: () =>
            h('div', { class: 'flex justify-between w-full' }, [
              h('span', 'Item 2'),
              h('i', { class: 'ri-arrow-right-line' }),
            ]),
        }),
      ])
  },
})

const AlertPreview = defineComponent({
  setup() {
    return () =>
      h('div', { class: 'space-y-2' }, [
        h(
          'button',
          {
            class: 'btn btn-success btn-sm',
            onClick: () =>
              showPush('Success', '', 'alert-success', 'ri-check-line'),
          },
          'Success'
        ),
        h(
          'button',
          {
            class: 'btn btn-error btn-sm',
            onClick: () =>
              showPush('Error', '', 'alert-error', 'ri-close-line'),
          },
          'Error'
        ),
      ])
  },
})

const EmptyPreview = defineComponent({
  setup() {
    return () =>
      h(
        'div',
        { class: 'text-sm opacity-60' },
        'No preview available'
      )
  },
})

const previewMap: Record<string, any> = {
  header: HeaderPreview,
  menu: MenuPreview,
  alert: AlertPreview,
}


const components: Record<ComponentKey, ComponentDef> = {
  header: {
    name: 'Header',
    code: `<Header :title="'Page Title'" :settings_show="true" />`,
  },
  menu: {
    name: 'Menu Card',
    code: `<Menu header="Section">
  <MenuCard>...</MenuCard>
</Menu>`,
  },
  alert: {
    name: 'Show Alert',
    code: `showPush('Success', '', 'alert-success', 'ri-check-line')`,
  },
  alerts: {
    name: 'Alerts',
    code: `<div class="alert alert-success">Success</div>`,
  },
  badges: {
    name: 'Badges',
    code: `<div class="badge badge-primary">Primary</div>`,
  },
  modals: {
    name: 'Modals',
    code: `<dialog class="modal">...</dialog>`,
  },
  inputs: {
    name: 'Inputs',
    code: `<input class="input input-bordered" />`,
  },
}

const current = computed(() => components[selected.value])
const currentPreview = computed(
  () => previewMap[selected.value] || EmptyPreview
)

/* ---------------- ACTIONS ---------------- */

async function copyCode() {
  if (!current.value?.code) return

  try {
    await navigator.clipboard.writeText(current.value.code)
    showPush('Copied', '', 'alert-success', 'ri-check-line')
  } catch {
    showPush('Copy failed', '', 'alert-error', 'ri-close-line')
  }
}
</script>

<template>
  <div class="flex flex-col min-h-full">
    <Header title="Components" />

    <div class="flex-1 grid md:grid-cols-2 gap-4 p-4 max-w-7xl mx-auto w-full">

      <!-- Preview -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-lg">Preview</h2>
          <div class="divider my-2" />

          <!-- Selector -->
          <div class="flex flex-wrap gap-2 mb-4">
            <button v-for="(comp, key) in components" :key="key" class="btn btn-sm"
              :class="selected === key ? 'btn-primary' : 'btn-ghost'" @click="selected = key">
              {{ comp.name }}
            </button>
          </div>

          <!-- Preview -->
          <div class="bg-base-200 rounded-lg p-4 min-h-64 flex items-center justify-center">
            <component :is="currentPreview" />
          </div>
        </div>
      </div>

      <!-- Code -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-lg">Code</h2>
          <div class="divider my-2" />

          <div class="bg-base-300 rounded-lg p-4 overflow-x-auto flex-1">
            <pre class="text-xs md:text-sm font-mono whitespace-pre-wrap break-words">
<code>{{ current.code }}</code>
            </pre>
          </div>

          <button class="btn btn-sm btn-outline mt-3 w-full" @click="copyCode">
            <i class="ri-file-copy-line" />
            Copy Code
          </button>
        </div>
      </div>

    </div>
  </div>
</template>