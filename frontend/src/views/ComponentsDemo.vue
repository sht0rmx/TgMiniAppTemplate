<script setup lang="ts">
import Header from '@/components/Header.vue'
import Card from '@/components/menu/Card.vue'
import Menu from '@/components/menu/Menu.vue'
import { showPush } from '@/utils/alert'
import { ref } from 'vue'

const selectedComponent = ref<string>('header')

interface ComponentDef {
  name: string
  code: string
}

const components: Record<string, ComponentDef> = {
  header: {
    name: 'Header',
    code: `<script setup lang="ts">
import Header from '@/components/Header.vue'
<\/script>

<!-- Basic Header -->
<Header :title="'Page Title'" :settings_show="true">
  <button class="tooltip tooltip-left"
    data-tip="Settings"
  >
    <i class="ri-settings-3-line text-2xl" />
  </button>
</Header>

<!-- Header with back button -->
<Header :title="'Page Title'">
  <button @click="$router.back()">
    <i class="ri-arrow-left-line text-2xl" />
  </button>
</Header>`,
  },
  menu: {
    name: 'Menu Card',
    code: `<script setup lang="ts">
import MenuCard from '@/components/menu/Card.vue'
import Menu from '@/components/menu/Menu.vue'
<\/script>

<!-- Menu with Cards -->
<Menu header="Section Title">
  <MenuCard>
    <template #content>
      <div class="flex w-full justify-between">
        <span>Item 1</span>
        <i class="ri-arrow-right-line" />
      </div>
    </template>
  </MenuCard>

  <MenuCard>
    <template #content>
      <div class="flex w-full justify-between">
        <span>Item 2</span>
        <i class="ri-arrow-right-line" />
      </div>
    </template>
  </MenuCard>
</Menu>`,
  },
  alert: {
    name: 'Show Alert',
    code: `<script setup lang="ts">
import { showPush } from '@/components/alert'
<\/script>

<!-- Success Alert -->
showPush(
  'Success message',
  '',
  'alert-success',
  'ri-check-line'
)

<!-- Error Alert -->
showPush(
  'Error message',
  '',
  'alert-error',
  'ri-close-line'
)

<!-- Warning Alert -->
showPush(
  'Warning message',
  '',
  'alert-warning',
  'ri-alert-line'
)

<!-- Info Alert -->
showPush(
  'Info message',
  '',
  'alert-info',
  'ri-information-line'
)`,
  },
  alerts: {
    name: 'Alerts',
    code: `<!-- Success Alert -->
<div class="alert alert-success">
  <i class="ri-check-line"></i>
  <span>Success message</span>
</div>

<!-- Error Alert -->
<div class="alert alert-error">
  <i class="ri-error-warning-line"></i>
  <span>Error message</span>
</div>

<!-- Warning Alert -->
<div class="alert alert-warning">
  <i class="ri-alert-line"></i>
  <span>Warning message</span>
</div>

<!-- Info Alert -->
<div class="alert alert-info">
  <i class="ri-information-line"></i>
  <span>Info message</span>
</div>`,
  },
  badges: {
    name: 'Badges',
    code: `<!-- Primary Badge -->
<div class="badge badge-primary">Primary</div>

<!-- Secondary Badge -->
<div class="badge badge-secondary">Secondary</div>

<!-- Success Badge -->
<div class="badge badge-success">Success</div>

<!-- Large Badge -->
<div class="badge badge-lg">Large</div>

<!-- Outline Badge -->
<div class="badge badge-outline">Outline</div>`,
  },
  modals: {
    name: 'Modals',
    code: `<!-- Basic Modal -->
    <Teleport to="body">
<dialog id="my_modal" class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">Modal Title</h3>
    <p class="py-4">Modal content</p>
    <div class="modal-action">
      <button
        class="btn"
        onclick="my_modal.close()"
      >
        Close
      </button>
    </div>
  </div>
</dialog>
</Teleport>

<!-- Open Modal -->
<button
  class="btn"
  onclick="my_modal.showModal()"
>
  Open Modal
</button>`,
  },
  inputs: {
    name: 'Inputs',
    code: `<!-- Text Input -->
<input
  type="text"
  placeholder="Enter text"
  class="input input-bordered w-full"
/>

<!-- Textarea -->
<textarea
  placeholder="Enter text"
  class="textarea textarea-bordered w-full"
></textarea>

<!-- Select -->
<select class="select select-bordered w-full">
  <option disabled selected>Pick one</option>
  <option>Option 1</option>
  <option>Option 2</option>
</select>

<!-- Checkbox -->
<input
  type="checkbox"
  class="checkbox"
/>

<!-- Radio -->
<input
  type="radio"
  name="radio"
  class="radio"
/>`,
  },
}

function copyCode(): void {
  const code = components[selectedComponent.value]?.code
  if (!code) return
  if (navigator.clipboard) {
    navigator.clipboard
      .writeText(code)
      .then(() => showPush('views.components_demo.copy_ok', '', 'alert-success', 'ri-check-line'))
      .catch(() => showPush('views.components_demo.copy_fail', '', 'alert-error', 'ri-close-line'))
  }
}
</script>

<template>
  <div class="flex flex-col min-h-full">
    <Header :title="$t('views.menu.components')" />

    <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 p-4 max-w-7xl mx-auto w-full">
      <!-- UI Preview -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-lg">{{ $t('views.components_demo.preview') }}</h2>
          <div class="divider my-2"></div>

          <!-- Component Selector -->
          <div class="flex flex-wrap gap-2 mb-4">
            <button v-for="(comp, key) in components" :key="key" class="btn btn-sm"
              :class="selectedComponent === key ? 'btn-primary' : 'btn-ghost'" @click="selectedComponent = key">
              {{ comp.name }}
            </button>
          </div>

          <!-- Preview Area -->
          <div class="bg-base-200 rounded-lg p-4 min-h-64 flex items-center justify-center">
            <!-- Header Preview -->
            <template v-if="selectedComponent === 'header'">
              <div class="w-full">
                <Header :title="$t('views.components_demo.page_title')" :settings_show="true" />
                <div class="p-4 text-sm text-base-content">
                  <p>{{ $t('views.components_demo.header_caption') }}</p>
                </div>
              </div>
            </template>

            <!-- Menu Preview -->
            <template v-if="selectedComponent === 'menu'">
              <div class="w-full">
                <Menu header="views.components_demo.menu_section">
                  <Card>
                    <template #content>
                      <div class="flex w-full justify-between">
                        <span>{{ $t('views.components_demo.menu_item_1') }}</span>
                        <i class="ri-arrow-right-line" />
                      </div>
                    </template>
                  </Card>
                  <Card>
                    <template #content>
                      <div class="flex w-full justify-between">
                        <span>{{ $t('views.components_demo.menu_item_2') }}</span>
                        <i class="ri-arrow-right-line" />
                      </div>
                    </template>
                  </Card>
                </Menu>
              </div>
            </template>

            <!-- Alert Preview -->
            <template v-if="selectedComponent === 'alert'">
              <div class="w-full space-y-3">
                <button class="btn btn-success btn-sm"
                  @click="showPush('views.components_demo.sample_success', '', 'alert-success', 'ri-check-line')">
                  {{ $t('views.components_demo.show_success') }}
                </button>
                <button class="btn btn-error btn-sm"
                  @click="showPush('views.components_demo.sample_error', '', 'alert-error', 'ri-close-line')">
                  {{ $t('views.components_demo.show_error') }}
                </button>
                <button class="btn btn-warning btn-sm"
                  @click="showPush('views.components_demo.sample_warning', '', 'alert-warning', 'ri-alert-line')">
                  {{ $t('views.components_demo.show_warning') }}
                </button>
                <button class="btn btn-info btn-sm"
                  @click="showPush('views.components_demo.sample_info', '', 'alert-info', 'ri-information-line')">
                  {{ $t('views.components_demo.show_info') }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Code -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-lg">{{ $t('views.components_demo.code') }}</h2>
          <div class="divider my-2"></div>

          <!-- Code Display -->
          <div class="bg-base-300 rounded-lg p-4 overflow-x-auto flex-1">
            <pre class="text-xs md:text-sm font-mono whitespace-pre-wrap break-word"><code>{{
              components[selectedComponent]?.code }}</code></pre>
          </div>

          <!-- Copy Button -->
          <button class="btn btn-sm btn-outline mt-3 w-full" @click="copyCode">
            <i class="ri-file-copy-line"></i>
            Copy Code
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
