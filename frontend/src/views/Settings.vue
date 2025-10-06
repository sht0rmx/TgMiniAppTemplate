<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { supported } from '@/locales/index.js'
import DropDownSelect from '@/components/DropDownSelect.vue'
import { apiClient } from '@/api/client.js'
import { useUserStore } from '@/store/user.js'
import { isTgEnv } from '@/main.js'

const badgeDb = ref('badge badge-outline badge-info')
const badgeAuth = ref('badge badge-outline badge-info')
const statusDb = ref('other.load')
const statusAuth = ref('other.load')
const username = ref('')
const store = useUserStore()

const isLogged = ref(!!apiClient.getAccessToken())

const { locale, t } = useI18n()
const router = useRouter()
const localeValue = ref(locale.value)

watch(localeValue, (val) => {
  if (val !== locale.value) {
    locale.value = val
    document.cookie = `lang=${val};path=/;max-age=31536000`
  }
})
async function handleLogout() {
  await apiClient.logout()
  isLogged.value = false
  await router.push('/need_auth')
}

async function checkAuth() {
  await apiClient.check()
  let user = store.user
  if (user && user.id) {
    username.value = user.username
    badgeAuth.value = 'badge badge-success'
    statusAuth.value = 'views.settings.badges.auth.ok'
  } else {
    username.value = ''
    badgeAuth.value = 'badge badge-error'
    statusAuth.value = 'views.settings.badges.auth.error'
  }
}

async function fetchStatus() {
  try {
    const status = await apiClient.ping()
    if (status) {
      badgeDb.value = 'badge badge-success'
      statusDb.value = 'views.settings.badges.api.success'
    } else {
      badgeDb.value = 'badge badge-error'
      statusDb.value = 'views.settings.badges.api.unavailable'
    }
  } catch (err) {
    console.error('ping failed:', err)
    badgeDb.value = 'badge badge-warning'
    statusDb.value = 'views.settings.badges.api.error'
  }
}

onMounted(() => {
  fetchStatus()
  checkAuth()
})
</script>

<template>
  <div class="flex flex-col space-y-2 mt-8 mb-8">
    <h1 class="text-4xl font-bold">{{ t('views.settings.header') }}</h1>
    <p class="text-gray-400 text-base">{{ t('views.settings.hint') }}</p>
  </div>

  <div class="flex flex-col w-full max-w mx-auto p-2 mb-8 gap-6">

    <div>
      <div class="flex flex-col space-y-2 mb-2 ml-1">
        <h2 class="text-sm font-semibold">{{ t('views.settings.general.name') }}</h2>
      </div>
      <ul class="list bg-base-100 rounded-box shadow-md w-full relative">
        <li>
          <span class="list-row items-center flex w-full">
            <i class="ri-translate text-3xl"></i>
            <div class="flex-1">{{ t('views.settings.general.language') }}</div>
            <DropDownSelect
              v-model="localeValue"
              :items="supported"
              :labelFn="(l) => t(`lang_select.${l}`)"
            />
          </span>
        </li>
      </ul>
    </div>

    <div>
      <div class="flex flex-col space-y-2 mb-2 ml-1">
        <h2 class="text-sm font-semibold">{{ t('views.settings.additional.name') }}</h2>
      </div>
      <ul class="list bg-base-100 rounded-box shadow-md w-full relative hover:bg-base-200">
        <li>
            <a href="https://github.com/sht0rmx/TgMiniAppTemplate" target="_blank" rel="noopener noreferrer" class="list-row items-center flex w-full">
            <i class="ri-github-fill text-3xl"/>
            <div class="flex-1">{{ t('views.settings.additional.authors') }}</div>
            <i class="ri-arrow-right-s-line"/>
          </a>
        </li>
        <li v-if="isLogged && isTgEnv">
          <a class="list-row items-center flex w-full" @click="$router.push('/settings/devices')">
            <i class="ri-device-line text-3xl"/>
            <div class="flex-1">{{ t('views.settings.additional.devices') }}</div>
            <i class="ri-arrow-right-s-line"/>
          </a>
        </li>
      </ul>
    </div>

    <div v-if="isLogged && !isTgEnv">
      <div class="flex flex-col space-y-2 mb-2 ml-1">
        <h2 class="text-sm font-bold">{{ t('views.settings.danger.name') }}</h2>
      </div>
      <ul class="list bg-error rounded-box shadow-md w-full relative hover:bg-warning">
        <li>
          <a @click="handleLogout" target="_blank" rel="noopener noreferrer" class="list-row items-center flex w-full">
            <i class="ri-logout-box-line text-3xl text-gray-950"/>
            <div class="flex-1 text-gray-950">{{ t('views.settings.danger.logout') }}</div>
            <i class="ri-arrow-right-s-line text-gray-950"/>
          </a>
        </li>
      </ul>
    </div>

  </div>

  <div class="text-center items-center text-sm text-gray-400 mt-5 space-y-2">
    {{ t('views.settings.end_hint') }}
  </div>

  <div class="text-center items-center text-sm text-gray-400 mt-2 space-x-2 flex justify-center gap-2">

    <div class="badge badge-sm cursor-pointer" :class="badgeDb" @click="fetchStatus()">
      {{ t(statusDb) }}
    </div>

    <div class="badge badge-sm cursor-pointer" :class="badgeAuth" @click="checkAuth()">
      {{ t(statusAuth) }} {{ username }}
    </div>

  </div>
</template>
