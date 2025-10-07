<script setup lang="ts">
import { ref, watch, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useI18n } from "vue-i18n"
import { supported } from "@/locales"
import { apiClient } from "@/api/client"
import { useUserStore } from "@/store/user"
import { isTgEnv } from "@/main"

// shadcn
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from '@/components/ui/card'
import { ButtonGroup } from '@/components/ui/button-group'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem
} from "@/components/ui/dropdown-menu"

const router = useRouter()
const store = useUserStore()
const { locale, t } = useI18n()

const localeValue = ref(locale.value)
const isLogged = ref(!!apiClient.getAccessToken())
const username = ref("")

const badgeDbVariant = ref<"default" | "destructive" | "secondary" | "outline">("outline")
const badgeAuthVariant = ref<"default" | "destructive" | "secondary" | "outline">("outline")
const statusDb = ref("other.load")
const statusAuth = ref("other.load")

watch(localeValue, val => {
  if (val !== locale.value) {
    locale.value = val
    document.cookie = `lang=${val};path=/;max-age=31536000`
  }
})

async function fetchStatus() {
  try {
    const ok = await apiClient.ping()
    badgeDbVariant.value = ok ? "default" : "destructive"
    statusDb.value = ok
      ? "views.settings.badges.api.success"
      : "views.settings.badges.api.unavailable"
  } catch (err) {
    console.error("ping failed:", err)
    badgeDbVariant.value = "secondary"
    statusDb.value = "views.settings.badges.api.error"
  }
}

async function checkAuth() {
  try {
    await apiClient.check()
  } catch (err) {
    console.error("check failed:", err)
  }

  const user = store.user
  if (user?.id) {
    username.value = user.username || ""
    badgeAuthVariant.value = "default"
    statusAuth.value = "views.settings.badges.auth.ok"
    isLogged.value = true
  } else {
    username.value = ""
    badgeAuthVariant.value = "destructive"
    statusAuth.value = "views.settings.badges.auth.error"
    isLogged.value = !!apiClient.getAccessToken()
  }
}

async function handleLogout() {
  try {
    await apiClient.logout()
  } catch (err) {
    console.error("logout failed:", err)
  }
  isLogged.value = false
  router.push("/need_auth")
}

onMounted(() => {
  fetchStatus()
  checkAuth()
})
</script>

<template>
  <div class="flex flex-col space-y-6 py-8 max-w-xl mx-auto">
    <div>
      <h1 class="text-4xl font-bold">{{ t("views.settings.header") }}</h1>
      <p class="text-muted-foreground">{{ t("views.settings.hint") }}</p>
    </div>

    <div>
      <h2 class="text-sm font-semibold mb-2">{{ t("views.settings.general.name") }}</h2>
      <Card class="shadow-sm">
        <div class="flex items-center justify-between px-4">
          <div class="flex items-center gap-3">
            <i class="ri-translate text-2xl text-muted-foreground"></i>
            <span>{{ t("views.settings.general.language") }}</span>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="outline" size="sm" class="gap-1">
                {{ t(`lang_select.${localeValue}`) }}
                <i class="ri-arrow-down-s-line text-lg"></i>
              </Button>
            </DropdownMenuTrigger>

            <DropdownMenuContent align="end" class="w-40">
              <DropdownMenuItem
                v-for="lang in supported"
                :key="lang"
                @click="localeValue = lang"
              >
                {{ t(`lang_select.${lang}`) }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </Card>
    </div>

    <div class="space-y-2">
      <h2 class="text-sm font-semibold">{{ t("views.settings.additional.name") }}</h2>

      <ButtonGroup
          orientation="vertical"
          aria-label="Media controls"
          class="h-fit"
        >
        <button
          as="a"
          href="https://github.com/sht0rmx/TgMiniAppTemplate"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center w-full py-3 text-left"
        >
          <i class="ri-github-fill text-2xl"></i>
          <span class="flex-1 text-sm">{{ t("views.settings.additional.authors") }}</span>
          <i class="ri-arrow-right-s-line text-lg"></i>
        </button>

        <button
          v-if="isLogged && isTgEnv"
          class="flex items-center w-full py-3 text-left"
          @click="router.push('/settings/devices')"
        >
          <i class="ri-device-line text-2xl"></i>
          <span class="flex-1 text-sm">{{ t("views.settings.additional.devices") }}</span>
          <i class="ri-arrow-right-s-line text-lg"></i>
        </button>
      </ButtonGroup>
    </div>

    <div v-if="isLogged && !isTgEnv">
      <h2 class="text-sm font-semibold mb-2 text-destructive">
        {{ t("views.settings.danger.name") }}
      </h2>
      <Card class="shadow-sm bg-destructive/10 hover:bg-destructive/20 transition">
        <button
          class="flex items-center w-full py-3 text-destructive"
          @click="handleLogout"
        >
          <i class="ri-logout-box-line text-2xl mr-3"></i>
          <span class="flex-1">{{ t("views.settings.danger.logout") }}</span>
          <i class="ri-arrow-right-s-line"></i>
        </button>
      </Card>
    </div>

    <div class="text-center text-sm text-muted-foreground mt-6">
      {{ t("views.settings.end_hint") }}
    </div>

    <div class="flex justify-center gap-4 mt-3">
      <Badge :variant="badgeDbVariant" class="cursor-pointer" @click="fetchStatus">
        {{ t(statusDb) }}
      </Badge>
      <Badge :variant="badgeAuthVariant" class="cursor-pointer" @click="checkAuth">
        {{ t(statusAuth) }}
        <span v-if="username" class="ml-1">({{ username }})</span>
      </Badge>
    </div>
  </div>
</template>
