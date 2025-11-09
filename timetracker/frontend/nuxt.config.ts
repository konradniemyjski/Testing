import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ['@pinia/nuxt', '@vueuse/nuxt'],
  css: ['@/assets/main.scss'],
  runtimeConfig: {
    apiBaseInternal:
      process.env.NUXT_API_BASE_INTERNAL ||
      process.env.NUXT_PUBLIC_API_BASE ||
      'http://localhost:8000',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },
  typescript: {
    strict: true,
    typeCheck: false
  }
})
