import { createI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { LanguagesService } from '@/utils/api/languages.api'

const LANG_KEY = 'lang'
const FALLBACK_LANG = 'en'

export type Locale = string

export const supportedLocales = ref<Locale[]>([FALLBACK_LANG])
export const currentLocale = ref<Locale>(detectLocale())

function detectLocale(): Locale {
  const saved = localStorage.getItem(LANG_KEY)
  const browser = navigator.language
  return normalizeLocale(saved || browser)
}

function normalizeLocale(value: string): Locale {
  return value?.split('-')[0] || FALLBACK_LANG
}

export const i18n = createI18n({
  legacy: false,
  locale: currentLocale.value,
  fallbackLocale: FALLBACK_LANG,
  messages: {},
})

const loaded = new Set<string>()

export const langs = computed(() =>
  supportedLocales.value.map(id => ({
    id,
    label: `lang_select.${id}`,
  })),
)

export async function loadLocaleMessages(locale: Locale) {
  if (loaded.has(locale)) return

  const messages = await LanguagesService.getLanguageMessages(locale)
  i18n.global.setLocaleMessage(locale, messages)
  loaded.add(locale)
}

export async function setLocale(locale: Locale) {
  const normalized = normalizeLocale(locale)

  await loadLocaleMessages(normalized)

  currentLocale.value = normalized
  i18n.global.locale.value = normalized
  localStorage.setItem(LANG_KEY, normalized)

  document.documentElement.lang = normalized
}

export async function fetchAvailableLocales() {
  try {
    const data = await LanguagesService.getLanguages()
    supportedLocales.value = data.map(item => item.id)

    if (!supportedLocales.value.includes(currentLocale.value)) {
      await setLocale(FALLBACK_LANG)
    }
  } catch {
    supportedLocales.value = [FALLBACK_LANG]
  }
}

export async function initializeLocale() {
  await fetchAvailableLocales()
  await setLocale(currentLocale.value)
}