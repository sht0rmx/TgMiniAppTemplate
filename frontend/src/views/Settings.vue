<script setup lang="ts">
import { AuthService } from '@/utils/api/auth.api'
import Header from '@/components/Header.vue'
import LoginCard from '@/components/LoginCard.vue'
import Menu from '@/components/menu/Menu.vue'
import MenuButton from '@/components/menu/Button.vue'
import MenuContent from '@/components/menu/Content.vue'
import MenuDropdown from '@/components/menu/Dropdown.vue'
import { ref, computed } from 'vue'
import { useUserStore } from '@/utils/stores/user'
import { useRouter } from 'vue-router'
import { showPush } from '@/components/alert'
import { WebApp } from '@/utils/telegram'
import { AccountService } from '@/utils/api/account.api'
import MenuCard from '@/components/menu/Card.vue'
import ConfirmationModal from '@/components/ConfirmationModal.vue'
import { useI18n } from 'vue-i18n'
import { setLocale, currentLocale, type Locale } from '@/utils/langs.ts'
import { authStatus, isTgEnv } from '@/main'
import { setTheme, currentTheme, type Theme } from '@/utils/themes.ts'

const { locale, t } = useI18n()

const appVersion = __APP_VERSION__
const buildHash = __BUILD_HASH__
const buildDate = new Date(__BUILD_DATE__).toLocaleDateString(locale.value, {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
})

const themes: { id: Theme; label: string; icon: string }[] = [
  { id: 'system', label: t('app.ui.system'), icon: 'ri-computer-line' },
  { id: 'dim', label: t('app.ui.dark'), icon: 'ri-moon-line' },
  { id: 'winter', label: t('app.ui.light'), icon: 'ri-sun-line' },
]

const langs: { id: Locale; label: string }[] = [
  { id: 'en', label: t('lang_select.en') },
  { id: 'ru', label: t('lang_select.ru') },
]

const logout = async () => {
  try {
    await AuthService.revokeRefreshSession()
    window.location.reload()
  } catch (error) {
    console.error('Logout failed', error)
  }
}

const router = useRouter()
const userStore = useUserStore()
const isDeleting = ref(false)
const isLinking = ref(false)
const showDeleteModal = ref(false)
const showUnlinkModal = ref(false)
const unlinkProvider = ref<'telegram' | 'yandex' | null>(null)
const linkedAccounts = computed(() => userStore.data?.linked_accounts || {})

const deleteAccount = async () => {
  showDeleteModal.value = true
}

const confirmDeleteAccount = async () => {
  isDeleting.value = true
  try {
    const success = await AccountService.deleteAccount()
    if (success) {
      showPush('User account deleted', '', 'alert-success', 'ri-check-line')
      await AuthService.revokeRefreshSession()
      userStore.clearUser()
      await router.push('/login')
    } else {
      showPush('Failed to delete account', '', 'alert-warning', 'ri-close-line')
    }
  } catch (error) {
    console.error('Delete account error:', error)
    showPush('Error deleting account', '', 'alert-warning', 'ri-close-line')
  } finally {
    isDeleting.value = false
    showDeleteModal.value = false
  }
}

const linkTelegram = async () => {
  if (!isTgEnv.value || !WebApp) {
    showPush('Not in Telegram environment', '', 'alert-warning', 'ri-error-warning-line')
    return
  }

  try {
    const token = await AccountService.getTelegramLinkingToken()
    if (!token) {
      showPush('Failed to get linking token', '', 'alert-warning', 'ri-close-line')
      return
    }

    const botUsername = import.meta.env.VITE_TG_USERNAME
    const startParam = `link_account_${token}`
    WebApp.openLink(`https://t.me/${botUsername}?start=${startParam}`)
  } catch (error) {
    console.error('Link Telegram error:', error)
    showPush('Error linking Telegram account', '', 'alert-warning', 'ri-close-line')
  }
}

const linkYandex = () => {
  const clientId = import.meta.env.VITE_YACID as string

  const url =
    `https://oauth.yandex.ru/authorize?response_type=code` +
    `&client_id=${clientId}` +
    `&state=link_account`

  window.location.href = url
}

const unlinkAccount = async (provider: 'telegram' | 'yandex') => {
  unlinkProvider.value = provider
  showUnlinkModal.value = true
}

const confirmUnlinkAccount = async () => {
  if (!unlinkProvider.value) return

  try {
    isLinking.value = true
    const success = await AccountService.unlinkAccount(unlinkProvider.value)
    if (success) {
      showPush(`${unlinkProvider.value} unlinked`, '', 'alert-success', 'ri-check-line')
      await AuthService.check()
    } else {
      showPush(`Failed to unlink ${unlinkProvider.value}`, '', 'alert-warning', 'ri-close-line')
    }
  } catch (error) {
    console.error(`Unlink ${unlinkProvider.value} error:`, error)
    showPush('Error unlinking account', '', 'alert-warning', 'ri-close-line')
  } finally {
    isLinking.value = false
    showUnlinkModal.value = false
    unlinkProvider.value = null
  }
}
</script>

<template>
  <Header :title="t('views.settings.title')" />

  <div class="flex flex-col gap-6 max-w-xl mx-auto">
    <LoginCard />

    <Menu header="views.settings.appearance">
      <MenuDropdown>
        <MenuButton
          tabindex="0"
          role="button"
          :text="$t('views.settings.appearance')"
          icon="ri-moon-clear-line"
        >
          <div class="flex items-center gap-2">
            <span class="text-sm text-accent uppercase font-semibold">
              {{ themes.find((theme) => theme.id === currentTheme)?.label }}
            </span>
          </div>
        </MenuButton>
        <MenuContent>
          <li class="flex flex-col gap-1">
            <button
              v-for="theme in themes"
              :key="theme.id"
              @click="setTheme(theme.id)"
              class="flex justify-between items-center py-2 px-4 rounded-lg"
              :class="
                currentTheme === theme.id ? 'bg-accent text-accent-content' : 'hover:bg-base-200'
              "
            >
              <div class="flex items-center gap-2">
                <i :class="theme.icon" />
                <span class="font-medium">{{ theme.label }}</span>
              </div>

              <i v-if="currentTheme === theme.id" class="ri-check-line" />
            </button>
          </li>
        </MenuContent>
      </MenuDropdown>

      <MenuDropdown>
        <MenuButton
          tabindex="0"
          role="button"
          :text="$t('views.settings.language')"
          icon="ri-translate"
        >
          <div class="flex items-center gap-2">
            <span class="text-sm text-accent uppercase font-semibold">
              {{ langs.find((lang) => lang.id === currentLocale)?.label }}
            </span>
          </div>
        </MenuButton>

        <MenuContent>
          <li class="flex flex-col gap-1">
            <button
              v-for="lang in langs"
              :key="lang.id"
              @click="setLocale(lang.id)"
              class="flex justify-between items-center py-2 px-4 rounded-lg"
              :class="
                lang.id === currentLocale ? 'bg-accent text-accent-content' : 'hover:bg-base-200'
              "
            >
              <span class="font-medium">{{ lang.label }}</span>
              <i v-if="lang.id === currentLocale" class="ri-check-line" />
            </button>
          </li>
        </MenuContent>
      </MenuDropdown>
    </Menu>

    <Menu header="views.settings.main" v-if="authStatus">
      <MenuButton
        :text="$t('views.settings.devices')"
        icon="ri-smartphone-line"
        @click="$router.push('/menu/settings/devices')"
      />
      <MenuButton
        :text="$t('views.settings.api_keys')"
        icon="ri-key-2-line"
        @click="$router.push('/menu/settings/apikey')"
      />
    </Menu>

    <Menu header="views.account.linked_accounts" v-if:="authStatus">
      <MenuCard>
        <template #content>
          <div class="flex w-full justify-between items-center">
            <div class="flex items-center gap-3">
              <i class="ri-telegram-2-line text-2xl text-blue-500" />
              <div>
                <div class="font-semibold">Telegram</div>
                <div class="text-xs text-base-content/60">
                  {{ linkedAccounts.telegram ? 'Linked' : 'Not linked' }}
                </div>
              </div>
            </div>

            <button
              v-if="linkedAccounts.telegram"
              class="btn btn-sm btn-outline btn-error"
              :disabled="isLinking"
              @click="unlinkAccount('telegram')"
            >
              <span v-if="isLinking" class="loading loading-spinner loading-sm"></span>
              <span v-else>{{ $t('actions.unlink') || 'Unlink' }}</span>
            </button>
            <button
              v-else
              class="btn btn-sm btn-primary"
              :disabled="isLinking"
              @click="linkTelegram"
            >
              <span v-if="isLinking" class="loading loading-spinner loading-sm"></span>
              <span v-else>{{ $t('actions.link') || 'Link' }}</span>
            </button>
          </div>
        </template>
      </MenuCard>
      <MenuCard>
        <template #content>
          <div class="flex w-full justify-between items-center">
            <div class="flex items-center gap-3">
              <i class="text-2xl text-red-500">Y</i>
              <div>
                <div class="font-semibold">Yandex</div>
                <div class="text-xs text-base-content/60">
                  {{ linkedAccounts.yandex ? 'Linked' : 'Not linked' }}
                </div>
              </div>
            </div>

            <button
              v-if="linkedAccounts.yandex"
              class="btn btn-sm btn-outline btn-error"
              :disabled="isLinking"
              @click="unlinkAccount('yandex')"
            >
              <span v-if="isLinking" class="loading loading-spinner loading-sm"></span>
              <span v-else>{{ $t('actions.unlink') || 'Unlink' }}</span>
            </button>
            <button v-else class="btn btn-sm btn-primary" :disabled="isLinking" @click="linkYandex">
              <span v-if="isLinking" class="loading loading-spinner loading-sm"></span>
              <span v-else>{{ $t('actions.link') || 'Link' }}</span>
            </button>
          </div>
        </template>
      </MenuCard>
    </Menu>

    <Menu header="views.settings.danger" v-if:="authStatus">
      <MenuButton
        @click="$router.push('/recovery')"
        icon="ri-shield-keyhole-line"
        :text="$t('views.settings.account_recovery')"
      />
      <MenuButton
        @click="deleteAccount"
        icon="ri-delete-bin-line"
        :text="$t('actions.delete_account')"
      >
        <span v-if="isDeleting" class="loading loading-spinner loading-sm"></span>
      </MenuButton>
      <MenuButton
        v-if:="!isTgEnv"
        @click="logout"
        text="views.settings.logout"
        icon="ri-logout-box-line"
      >
        <i class="ri-arrow-right-s-line text-xl opacity-50"></i>
      </MenuButton>
    </Menu>

    <div class="flex flex-col items-center gap-1 pb-2 opacity-50 select-none">
      <p class="text-xs font-medium">
        {{ t('views.settings.version', { version: appVersion }) }}
      </p>
      <p class="text-xs font-mono">{{ buildHash }} &middot; {{ buildDate }}</p>
    </div>

    <ConfirmationModal
      :is-open="showDeleteModal"
      title="views.settings.delete_confirm_title"
      message="views.settings.delete_confirm_message"
      confirm-text="actions.delete_account"
      confirm-button-class="btn-error"
      :is-loading="isDeleting"
      @confirm="confirmDeleteAccount"
      @cancel="showDeleteModal = false"
    />

    <ConfirmationModal
      v-if="unlinkProvider"
      :is-open="showUnlinkModal"
      :title="`views.settings.unlink_confirm_title`"
      :message="`views.settings.unlink_confirm_message`"
      :confirm-text="`actions.unlink`"
      confirm-button-class="btn-warning"
      :is-loading="isLinking"
      @confirm="confirmUnlinkAccount"
      @cancel="showUnlinkModal = false"
    />
  </div>
</template>
