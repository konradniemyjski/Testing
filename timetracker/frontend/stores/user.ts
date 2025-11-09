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

export const useUserStore = defineStore('user', {
  state: () => ({
    accessToken: '' as string,
    profile: null as UserProfile | null
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken)
  },
  actions: {
    setCredentials(token: string, profile: UserProfile) {
      this.accessToken = token
      this.profile = profile
    },
    clear() {
      this.accessToken = ''
      this.profile = null
    }
  }
})

export async function login(email: string, password: string) {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

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

export async function register(payload: { email: string; password: string; full_name?: string; role?: 'user' | 'admin' }) {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  await $fetch(`${apiBase}/auth/register`, {
    method: 'POST',
    body: payload
  })
}
