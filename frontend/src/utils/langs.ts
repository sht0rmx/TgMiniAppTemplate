import en from '@/locales/en.json'
import ru from '@/locales/ru.json'
import { createI18n } from 'vue-i18n'
import { ref, type Ref} from 'vue'

const LANG_KEY = "lang"
const FALLBACK_LANG: Locale = "en"
export type Locale = "en" | "ru"

interface MessageSchema {
  [key: string]: any
}

let web_locale: string = navigator.language.split('-')[0]!
export let currentLocale: Ref<string | null> = ref(localStorage.getItem(LANG_KEY) as Locale || web_locale as Locale || FALLBACK_LANG)

export function setLocale(locale: string) {
  localStorage.setItem(LANG_KEY, locale as Locale)
  currentLocale.value = locale as Locale
  i18n.global.locale = locale as Locale
}

const i18n = createI18n({
  locale: currentLocale.value as Locale,
  fallbackLocale: FALLBACK_LANG,
  messages: {
    en: en as MessageSchema,
    ru: ru as MessageSchema,
  },
})

export { i18n }
