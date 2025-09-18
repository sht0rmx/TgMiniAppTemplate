<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const badgeDb = ref('badge-outline badge-info')
const badgeAuth = ref('badge-outline badge-info')
const status = ref(t('views.settings.badges.api.unvl'))
const status_auth = ref('...')

async function checkAuth() {
    const ok = false

    if (ok) {
        const user = pb.authStore.record
        const uname = user?.username || user?.email || "unknown"

        badgeAuth.value = "badge-success"
        status_auth.value = t('views.settings.badges.auth.ok', { uname })
    } else {
        badgeAuth.value = "badge-error"
        status_auth.value = t('views.settings.badges.auth.err')
    }
}

async function fetchStatus() {
    try {
        const result = { code: 505 }

        if (result.code !== 200) {
            badgeDb.value = 'badge badge-error'
            status.value = t('views.settings.badges.api.unvl')
        } else {
            badgeDb.value = 'badge badge-success'
            status.value = t('views.settings.badges.api.succ')
        }
    } catch (error) {
        console.error('Failed to fetch db status:', error)
        badgeDb.value = "badge-warning"
        status.value = t('views.settings.badges.api.err')
    }
}

fetchStatus()
checkAuth()
</script>


<template>
    <div class="flex flex-col space-y-2 mt-8 mb-12">
        <h1 class="text-4xl font-bold">
            Settings
        </h1>
        <p class="text-gray-400 text-base">{{ $t("views.settings.hint") }}</p>
    </div>
    <div class="flex flex-col w-full max-w- mx-auto p-2 mb-10">
        <ul class="list bg-base-100 rounded-box shadow-md w-full relative hover:bg-base-200">
            <li>
                <a href="https://github.com/sht0rmx/TgMiniAppTemplate" target="_blank" rel="noopener noreferrer"
                    class="list-row items-center flex w-full">
                    <i class="ri-github-fill text-2xl"></i>
                    <div class="flex-1">{{ $t("views.settings.authors") }}</div>
                    <i class="ri-arrow-right-s-line"></i>
                </a>
            </li>
        </ul>

    </div>
    <div class="text-center items-center text-sm text-gray-400 mt-5 space-y-2">
        {{ $t("views.settings.end_hint") }}
    </div>
    <div class="text-center items-center text-sm text-gray-400 mt-2 space-x-2">
        <div class="badge badge-sm" :class="badgeDb" @click="fetchStatus();">{{ status }}</div>
        <div class="badge badge-sm" :class="badgeAuth" @click="checkAuth();">{{ status_auth }}</div>
    </div>
</template>