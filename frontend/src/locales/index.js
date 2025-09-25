import en from './lo/en.json'
import ru from './lo/ru.json'
import { createI18n } from 'vue-i18n'

function getLangFromCookie() {
  const match = document.cookie.match(/(?:^|;\s*)lang=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : null
}

const savedLocale = getLangFromCookie()

const userLocale = savedLocale || navigator.language || navigator.userLanguage
const locale = userLocale.split('-')[0]

export const supported = ['en', 'ru']
const finalLocale = supported.includes(locale) ? locale : 'en'

const messages = {
  en,
  ru,
}

const i18n = createI18n({
  legacy: false,
  locale: finalLocale,
  fallbackLocale: 'en',
  messages,
})

export { i18n }
