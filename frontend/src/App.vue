<template>
  <div :class="['flex flex-col min-h-screen bg-base-200', { 'pb-14': $route.path !== '/need_auth' }]">
    
    <main :class="['flex-1 text-sm text-base-content flex justify-center', { 'p-4': $route.path !== '/need_auth' }]">
      <div :class="[
        'w-full',
        $route.path === '/need_auth' ? 'max-w-sm' : 'max-w-2xl'
      ]">
        <router-view />
      </div>
    </main>

    <BottomDock v-if="$route.path !== '/need_auth'"/>
  </div>
</template>

<script setup>
import BottomDock from '@/components/BottomDock.vue'
import { onMounted } from 'vue'
import { TgApp, isTgEnv } from './main'
import pb from '@/pocketbase'

onMounted(async () => {
  if (isTgEnv && TgApp) {
    try {
      const res = await fetch(`${import.meta.env.VITE_POCKETBASE_URL}/api/auth/telegram`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData: TgApp.initData })
      })
      if (!res.ok) throw new Error('Auth request failed')
      const data = await res.json()

      pb.authStore.save(data.token, data.record)
      console.log('PB auth success:', pb.authStore.isValid)
    } catch (err) {
      console.error('PB auth failed:', err)
    }
  } else {
    console.warn('Not inside Telegram WebApp')
  }
})
</script>
