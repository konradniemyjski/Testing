import { useUserStore } from '~/stores/user'

export function useApi() {
  const config = useRuntimeConfig()
  const userStore = useUserStore()
  const router = useRouter()
  const apiBase = process.server
    ? config.apiBaseInternal ?? config.public.apiBase
    : config.public.apiBase

  return async <T>(endpoint: string, options: Parameters<typeof $fetch<T>>[1] = {}) => {
    if (process.client && !userStore.hydrated) {
      userStore.hydrateFromStorage()
    }

    const headers = new Headers(options?.headers as HeadersInit | undefined)
    if (userStore.accessToken) {
      headers.set('Authorization', `Bearer ${userStore.accessToken}`)
    }

    try {
      return await $fetch<T>(`${apiBase}${endpoint}`, {
        ...options,
        headers: Object.fromEntries(headers.entries()),
        retry: false
      })
    } catch (error: any) {
      const statusCode = error?.statusCode ?? error?.response?.status ?? error?.status
      if (statusCode === 401) {
        userStore.clear()
        if (process.client) {
          router.replace('/login')
        }
      }
      throw error
    }
  }
}
