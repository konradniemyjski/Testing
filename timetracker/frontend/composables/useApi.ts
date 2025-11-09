import { useUserStore } from '~/stores/user'

export function useApi() {
  const config = useRuntimeConfig()
  const userStore = useUserStore()
  const apiBase = process.server
    ? config.apiBaseInternal ?? config.public.apiBase
    : config.public.apiBase

  return async <T>(endpoint: string, options: Parameters<typeof $fetch<T>>[1] = {}) => {
    const headers = new Headers(options?.headers as HeadersInit | undefined)
    if (userStore.accessToken) {
      headers.set('Authorization', `Bearer ${userStore.accessToken}`)
    }

    return $fetch<T>(`${apiBase}${endpoint}`, {
      ...options,
      headers
    })
  }
}
