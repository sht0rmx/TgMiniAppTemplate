import en from './lo/en.json'
import ru from './lo/ru.json'
import {createI18n} from "vue-i18n";

const userLocale = navigator.language || navigator.userLanguage
const locale = userLocale.split('-')[0]

const messages = {
    en,
    ru
}

const i18n = createI18n({
    legacy: false,
    locale: locale,
    fallbackLocale: 'en',
    messages
})

export { i18n };