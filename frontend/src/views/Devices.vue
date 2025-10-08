<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import {
  Drawer,
  DrawerTrigger,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
  DrawerFooter,
  DrawerClose,
} from '@/components/ui/drawer'
import List from '@/components/ui/list/List.vue'

const devices = ref([
  { icon: 'ri-smartphone-line', name: 'Pixel 8', ip: '192.168.0.12', last: '2025-10-08 17:42' },
  { icon: 'ri-macbook-line', name: 'MacBook Pro', ip: '10.0.0.15', last: '2025-10-07 22:10' },
  { icon: 'ri-tablet-line', name: 'iPad Air', ip: '172.19.0.5', last: '2025-10-08 09:33' },
])

const selectedDevice = ref(null)
const drawerOpen = ref(false)

const openDrawer = (device: any) => {
  selectedDevice.value = device
  drawerOpen.value = true
}

const closeSession = () => {
  drawerOpen.value = false
  selectedDevice.value = null
  console.log('Session closed')
}
</script>

<template>
  <div class="flex flex-col max-w-xl mx-auto space-y-8">
    <div class="text-center space-y-1 mb-3">
      <i class="ri-mac-line text-8xl text-chart-3"></i>
      <h1 class="text-4xl font-bold">{{ $t('views.devices.header') }}</h1>
      <p class="text-muted-foreground text-sm">{{ $t('views.devices.hint') }}</p>
    </div>

    <div class="flex w-full justify-center">
    <Button class="w-3/4 py-6">
      <i class="ri-loader-3-line text-xl leading-none"></i>
      <span class="p-2 text-semibold">{{ $t('views.devices.link') }}</span>
    </Button>
    </div>

    <List :title="$t('views.devices.this_device')">
      <button class="list-item" @click="openDrawer(d)">
        <i class="ri-smartphone-line text-2xl mr-3"></i>
        <div class="flex-1 text-sm">
          <div class="font-medium">Pixel 8</div>
          <div class="text-xs text-muted-foreground">172.19.0.5 • 2025-10-08 09:33</div>
        </div>
        <i class="ri-arrow-right-s-line text-lg text-muted-foreground"></i>
      </button>
    </List>

    <List :title="$t('views.devices.active')">
      <button v-for="(d, i) in devices" :key="i" class="list-item" @click="openDrawer(d)">
        <i :class="[d.icon, 'text-2xl mr-3']"></i>
        <div class="flex-1 text-sm">
          <div class="font-medium">{{ d.name }}</div>
          <div class="text-xs text-muted-foreground">{{ d.ip }} • {{ d.last }}</div>
        </div>
        <i class="ri-arrow-right-s-line text-lg text-muted-foreground"></i>
      </button>
    </List>

    <Drawer v-model:open="drawerOpen">
      <DrawerContent>
        <div class="flex flex-col w-full max-w-sm mx-auto">
          <DrawerHeader>
            <DrawerTitle class="flex flex-col items-center text-center mb-2">
              <div
                class="flex-shrink-0 w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-xl"
              >
                <i :class="selectedDevice?.icon" class="text-5xl"></i>
              </div>
              <div class="text-2xl">{{ selectedDevice?.name }}</div>
            </DrawerTitle>
            <DrawerDescription class="text-sm text-muted-foreground">
              <div>{{ $t('views.devices.dropdown.ip') }}: {{ selectedDevice?.ip }}</div>
              <div>{{ $t('views.devices.dropdown.last_seen') }}: {{ selectedDevice?.last }}</div>
            </DrawerDescription>
          </DrawerHeader>

          <DrawerFooter class="flex flex-row gap-2">
            <Button variant="destructive" class="flex-[2] min-w-0" @click="closeSession">
              {{ $t('views.devices.dropdown.terminate') }}
            </Button>
            <DrawerClose as-child>
              <Button variant="outline" class="flex-1 min-w-0">Закрыть</Button>
            </DrawerClose>
          </DrawerFooter>
        </div>
      </DrawerContent>
    </Drawer>
  </div>
</template>
