import { defineStore } from 'pinia'

type UserProfile = {
  id: number
  email: string
  full_name?: string | null
  role: 'user' | 'admin'
}

type TokenResponse = {
  access_token: string
  token_type: string
}

const TOKEN_STORAGE_KEY = 'worklog.accessToken'
const PROFILE_STORAGE_KEY = 'worklog.profile'

export const useUserStore = defineStore('user', {
  state: () => ({
    accessToken: '' as string,
    profile: null as UserProfile | null,
    hydrated: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken)
  },
  actions: {
    hydrateFromStorage() {
      if (this.hydrated || !process.client) {
        return
      }

      const storedToken = window.localStorage.getItem(TOKEN_STORAGE_KEY)
      const storedProfile = window.localStorage.getItem(PROFILE_STORAGE_KEY)

      if (storedToken) {
        this.accessToken = storedToken
      }

      if (storedProfile) {
        try {
          this.profile = JSON.parse(storedProfile) as UserProfile
        } catch {
          this.profile = null
        }
      }

      this.hydrated = true
    },
    setCredentials(token: string, profile: UserProfile) {
      this.accessToken = token
      this.profile = profile
      this.hydrated = true

      if (process.client) {
        window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
        window.localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile))
      }
    },
    clear() {
      this.accessToken = ''
      this.profile = null
      if (process.client) {
        window.localStorage.removeItem(TOKEN_STORAGE_KEY)
        window.localStorage.removeItem(PROFILE_STORAGE_KEY)
      }
    }
  }
})

export async function login(email: string, password: string) {
  const config = useRuntimeConfig()
  const apiBase = process.server
    ? config.apiBaseInternal ?? config.public.apiBase
    : config.public.apiBase

  const tokenResponse = await $fetch<TokenResponse>(`${apiBase}/auth/token`, {
    method: 'POST',
    body: new URLSearchParams({
      username: email,
      password
    }),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })

  const profile = await $fetch<UserProfile>(`${apiBase}/auth/me`, {
    headers: {
      Authorization: `Bearer ${tokenResponse.access_token}`
    }
  })

  const store = useUserStore()
  store.setCredentials(tokenResponse.access_token, profile)
}

export async function register(payload: { email: string; password: string; full_name?: string }) {
  const config = useRuntimeConfig()
  const apiBase = process.server
    ? config.apiBaseInternal ?? config.public.apiBase
    : config.public.apiBase

  await $fetch(`${apiBase}/auth/register`, {
    method: 'POST',
    body: payload
  })
}
