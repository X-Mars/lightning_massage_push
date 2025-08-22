/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_NODE_ENV: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_DEBUG: string
  readonly VITE_APP_VERSION: string
  readonly VITE_ENV_NAME: string
  readonly VITE_ENV_DISPLAY_NAME: string
  readonly VITE_LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error'
  readonly VITE_USE_MOCK: string
  readonly VITE_WS_BASE_URL: string
  readonly VITE_UPLOAD_SIZE_LIMIT: string
  readonly VITE_SHOW_ENV_TAG: string
  readonly VITE_DEV_TOOLS: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_ENABLE_PERFORMANCE: string
  readonly VITE_CDN_URL: string
  readonly VITE_ENABLE_ERROR_REPORTING: string
  readonly VITE_SENTRY_DSN: string
  readonly VITE_ENABLE_ANALYTICS: string
  readonly VITE_TEST_MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 全局常量
declare const __APP_VERSION__: string
declare const __BUILD_TIME__: string
