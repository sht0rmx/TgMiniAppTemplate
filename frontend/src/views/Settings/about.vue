<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ping, fetchUserProfile } from '@/utils/apiclient'

const { t } = useI18n()

const badgeDb = ref('badge badge-outline badge-info')
const badgeAuth = ref('badge badge-outline badge-info')
const statusDb = ref('...')
const statusAuth = ref('...')

async function checkAuth() {
  try {
    const user = await fetchUserProfile()
    if (user && user.id) {
      badgeAuth.value = 'badge badge-success'
      statusAuth.value = t('views.settings.subviews.about.badges.auth.ok', { uname: user.username || user.name })
    } else {
      badgeAuth.value = 'badge badge-error'
      statusAuth.value = t('views.settings.subviews.about.badges.auth.err')
    }
  } catch (err) {
    console.error('Auth check failed:', err)
    badgeAuth.value = 'badge badge-error'
    statusAuth.value = t('views.settings.subviews.about.badges.auth.err')
  }
}

async function fetchStatus() {
  try {
    const ok = await ping()
    if (ok) {
      badgeDb.value = 'badge badge-success'
      statusDb.value = t('views.settings.subviews.about.badges.api.succ')
    } else {
      badgeDb.value = 'badge badge-error'
      statusDb.value = t('views.settings.subviews.about.badges.api.unvl')
    }
  } catch (err) {
    console.error('DB ping failed:', err)
    badgeDb.value = 'badge badge-warning'
    statusDb.value = t('views.settings.subviews.about.badges.api.err')
  }
}

onMounted(() => {
  fetchStatus()
  checkAuth()
})
</script>

<template>
  <div class="flex flex-col space-y-2 mt-8 mb-12">
    <h1 class="text-4xl font-bold">{{ t("views.settings.subviews.about.title") }}</h1>
    <p class="text-gray-400 text-base">{{ t("views.settings.subviews.about.hint") }}</p>
  </div>

  <div class="flex flex-col w-full max-w- mx-auto p-2 mb-10">
    <ul class="list bg-base-100 rounded-box shadow-md w-full relative hover:bg-base-200">
      <li>
        <a href="https://github.com/sht0rmx/TgMiniAppTemplate" target="_blank" rel="noopener noreferrer"
           class="list-row items-center flex w-full">
          <i class="ri-github-fill text-2xl"></i>
          <div class="flex-1">{{ t("views.settings.subviews.about.authors") }}</div>
          <i class="ri-arrow-right-s-line"></i>
        </a>
      </li>
    </ul>
  </div>

  <div class="text-center items-center text-sm text-gray-400 mt-5 space-y-2">
    {{ t("views.settings.subviews.about.end_hint") }}
  </div>

  <div class="text-center items-center text-sm text-gray-400 mt-2 space-x-2 flex justify-center gap-2">
    <div class="badge badge-sm cursor-pointer" :class="badgeDb" @click="fetchStatus()">{{ statusDb }}</div>
    <div class="badge badge-sm cursor-pointer" :class="badgeAuth" @click="checkAuth()">{{ statusAuth }}</div>
  </div>
</template>
