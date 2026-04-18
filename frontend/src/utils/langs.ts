import { createI18n } from 'vue-i18n'
import { ref, type Ref } from 'vue'
import { LanguagesService } from '@/utils/api/languages.api.ts'

const LANG_KEY = 'lang'
const FALLBACK_LANG = 'en'

interface MessageSchema {
  [key: string]: any
}

export type Locale = string

export const supportedLocales: Ref<Locale[]> = ref([FALLBACK_LANG])

function normalizeLocale(locale: string): Locale {
  return locale.split('-')[0] || FALLBACK_LANG
}

const browserLocale = navigator.language.split('-')[0] || FALLBACK_LANG
const initialLocale = (localStorage.getItem(LANG_KEY) as string) || browserLocale

export let currentLocale: Ref<Locale> = ref(normalizeLocale(initialLocale))

const i18n = createI18n({
  locale: currentLocale.value,
  fallbackLocale: FALLBACK_LANG,
  messages: {},
})

export async function loadLocaleMessages(locale: string): Promise<void> {
  const normalized = normalizeLocale(locale)

  const messages = await LanguagesService.getLanguageMessages(normalized)
  i18n.global.setLocaleMessage(normalized, messages as MessageSchema)
}

export async function setLocale(locale: string): Promise<void> {
  const normalized = normalizeLocale(locale)
  await loadLocaleMessages(normalized)
  localStorage.setItem(LANG_KEY, normalized)
  currentLocale.value = normalized
  i18n.global.locale = normalized
}

export async function initializeLocale(): Promise<void> {
  try {
    await loadLocaleMessages(currentLocale.value)
  } catch (error) {
    if (currentLocale.value !== FALLBACK_LANG) {
      currentLocale.value = FALLBACK_LANG
      await loadLocaleMessages(FALLBACK_LANG)
    }
  }
}

export async function fetchAvailableLocales(): Promise<Locale[]> {
  try {
    const response = await LanguagesService.getLanguages()
    const ids = response.map((language) => language.id)

    supportedLocales.value = ids

    if (!supportedLocales.value.includes(currentLocale.value)) {
      await setLocale(FALLBACK_LANG)
    }

    return supportedLocales.value
  } catch (error) {
    console.warn('Failed to fetch available languages from backend:', error)
    return supportedLocales.value
  }
}

export { i18n }
