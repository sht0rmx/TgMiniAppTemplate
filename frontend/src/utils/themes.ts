import { ref, type Ref } from 'vue'

export type Theme = 'system' | 'default' | 'dim' | 'nord'

export const currentTheme: Ref<Theme> = ref('system')
const THEME_KEY = 'theme'

export const applyTheme = (theme: Theme) => {
  const resolved =
    theme === 'system'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dim'
        : 'default'
      : theme

  document.documentElement.setAttribute('data-theme', resolved)
}

export const setTheme = (theme: Theme = (localStorage.getItem(THEME_KEY) as Theme) || 'system') => {
  currentTheme.value = theme || localStorage.setItem(THEME_KEY, theme)
  applyTheme(theme)
}
