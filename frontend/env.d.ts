/// <reference types="vite/client" />

declare const __APP_VERSION__: string
declare const __BUILD_HASH__: string
declare const __BUILD_DATE__: string

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
