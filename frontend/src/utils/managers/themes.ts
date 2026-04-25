import { ref, type Ref } from 'vue'

export const themes = [
  {
    id: 'system',
    labelKey: 'app.ui.system',
    icon: 'ri-computer-line',
  },
  {
    id: 'simple-light',
    labelKey: 'app.ui.light',
    icon: 'ri-sun-line',
  },
  {
    id: 'simple-dark',
    labelKey: 'app.ui.dark',
    icon: 'ri-moon-line',
  },
] as const

export type Theme = (typeof themes)[number]['id']

const STORAGE_KEY = 'theme'
const DARK_THEME: Theme = 'simple-dark'
const LIGHT_THEME: Theme = 'simple-light'

export const currentTheme: Ref<Theme> = ref('system')

export const applyTheme = (theme: Theme) => {
  const resolved =
    theme === 'system'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
        ? DARK_THEME
        : LIGHT_THEME
      : theme

  document.documentElement.setAttribute('data-theme', resolved)
}

export const setTheme = (theme?: Theme) => {
  const value = theme ?? (localStorage.getItem(STORAGE_KEY) as Theme) ?? 'system'
  currentTheme.value = value
  localStorage.setItem(STORAGE_KEY, value)
  applyTheme(value)
}