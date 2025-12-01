import { defineNuxtConfig } from 'nuxt/config'

const publicApiBaseEnv = process.env.NUXT_PUBLIC_API_BASE
const internalApiBaseEnv = process.env.NUXT_API_BASE_INTERNAL

const fallbackPublicApiBase =
  publicApiBaseEnv !== undefined
    ? publicApiBaseEnv
    : process.env.NODE_ENV === 'development'
      ? 'http://localhost:8000'
      : ''

const fallbackInternalApiBase =
  internalApiBaseEnv !== undefined
    ? internalApiBaseEnv
    : publicApiBaseEnv !== undefined
      ? publicApiBaseEnv
      : 'http://backend:8000'

export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ['@pinia/nuxt', '@vueuse/nuxt'],
  css: ['@/assets/main.scss'],
  runtimeConfig: {
    apiBaseInternal: fallbackInternalApiBase,
    public: {
      apiBase: fallbackPublicApiBase
    }
  },
  typescript: {
    strict: true,
    typeCheck: false
  }
})
