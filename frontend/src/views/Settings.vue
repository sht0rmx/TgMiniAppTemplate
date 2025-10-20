<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { supported } from '@/locales'
import { apiClient } from '@/api/client'
import { useUserStore } from '@/store/user'
import { isTgEnv } from '@/main'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu'
import List from '@/components/ui/list/List.vue'

const router = useRouter()
const store = useUserStore()
const { locale, t } = useI18n()

const localeValue = ref(locale.value)
const isLogged = ref(!!apiClient.getAccessToken())
const username = ref('')

const badgeDbVariant = ref<'default' | 'destructive' | 'secondary' | 'outline'>('outline')
const badgeAuthVariant = ref<'default' | 'destructive' | 'secondary' | 'outline'>('outline')
const statusDb = ref('other.load')
const statusAuth = ref('other.load')

watch(localeValue, (val) => {
  if (val !== locale.value) {
    locale.value = val
    document.cookie = `lang=${val};path=/;max-age=31536000`
  }
})

async function fetchStatus() {
  try {
    const ok = await apiClient.ping()
    badgeDbVariant.value = ok ? 'default' : 'destructive'
    statusDb.value = ok
      ? 'views.settings.badges.api.success'
      : 'views.settings.badges.api.unavailable'
  } catch (err) {
    console.error('ping failed:', err)
    badgeDbVariant.value = 'secondary'
    statusDb.value = 'views.settings.badges.api.error'
  }
}

async function checkAuth() {
  try {
    await apiClient.check()
  } catch (err) {
    console.error('check failed:', err)
  }

  const user = store.user
  if (user?.id) {
    username.value = user.username || ''
    badgeAuthVariant.value = 'default'
    statusAuth.value = 'views.settings.badges.auth.ok'
    isLogged.value = true
  } else {
    username.value = ''
    badgeAuthVariant.value = 'destructive'
    statusAuth.value = 'views.settings.badges.auth.error'
    isLogged.value = !!apiClient.getAccessToken()
  }
}

async function handleLogout() {
  try {
    await apiClient.logout()
  } catch (err) {
    console.error('logout failed:', err)
  }
  isLogged.value = false
  router.push('/need_auth')
}

onMounted(() => {
  fetchStatus()
  checkAuth()
})
</script>

<template>
  <div class="flex flex-col max-w-xl mx-auto space-y-8 text-cbase">
    <div class="text-center space-y-1 mb-3">
      <i class="ri-settings-line text-8xl text-accent"></i>
      <h1 class="text-4xl font-bold">
        {{ t('views.settings.header') }}
      </h1>
      <p class="text-muted-foreground text-sm">
        {{ t('views.settings.hint') }}
      </p>
    </div>

    <List :title="t('views.settings.general.name')">
      <div class="list-item justify-between">
        <div class="flex items-center gap-3">
          <i class="ri-translate text-2xl"></i>
          <span class="text-sm font-medium">
            {{ t('views.settings.general.language') }}
          </span>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="secondary" size="sm" class="gap-1 flex items-center text-accent border border-border">
              {{ t(`lang_select.${localeValue}`) }}
              <i class="ri-arrow-down-s-line text-lg"></i>
            </Button>
          </DropdownMenuTrigger>

          <DropdownMenuContent
            align="end"
            class="w-44 bg-card text-card-foreground border border-border rounded-md shadow-md"
          >
            <DropdownMenuItem
              v-for="lang in supported"
              :key="lang"
              @click="localeValue = lang"
              class="text-sm text-cbase hover:bg-card-light hover:text-card-foreground"
            >
              {{ t(`lang_select.${lang}`) }}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </List>

    <List :title="t('views.settings.additional.name')">
      <button
        as="a"
        href="https://github.com/sht0rmx/TgMiniAppTemplate"
        target="_blank"
        rel="noopener noreferrer"
        class="list-item"
      >
        <i class="ri-github-fill text-2xl mr-3"></i>
        <span class="flex-1 text-sm font-medium">
          {{ t('views.settings.additional.authors') }}
        </span>
        <i class="ri-arrow-right-s-line text-lg"></i>
      </button>
      <button
        v-if="isLogged && isTgEnv"
        class="list-item"
        @click="router.push('/settings/devices')"
      >
        <i class="ri-device-line text-2xl mr-3"></i>
        <span class="flex-1 text-sm font-medium">
          {{ t('views.settings.additional.devices') }}
        </span>
        <i class="ri-arrow-right-s-line text-lg"></i>
      </button>
    </List>

    <List v-if="isLogged && !isTgEnv" :title="t('views.settings.danger.name')">
      <button class="list-item" @click="handleLogout">
        <i class="ri-logout-box-line text-2xl mr-3"></i>
        <span class="flex-1 text-sm font-medium">
          {{ t('views.settings.danger.logout') }}
        </span>
        <i class="ri-arrow-right-s-line"></i>
      </button>
    </List>

    <div class="text-center text-sm text-muted-foreground mt-8">
      {{ t('views.settings.end_hint') }}
      <div class="flex justify-center gap-4 mt-3">
        <Badge :variant="badgeDbVariant" class="cursor-pointer text-xs" @click="fetchStatus">
          {{ t(statusDb) }}
        </Badge>

        <Badge :variant="badgeAuthVariant" class="cursor-pointer text-xs" @click="checkAuth">
          {{ t(statusAuth) }}
          <span v-if="username" class="ml-1">{{ username }}</span>
        </Badge>
      </div>
    </div>
  </div>
</template>
