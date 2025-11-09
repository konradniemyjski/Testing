import { useUserStore } from '~/stores/user'

export default defineNuxtRouteMiddleware(() => {
  const userStore = useUserStore()
  const destination = userStore.isAuthenticated ? '/dashboard' : '/login'
  if (process.client) {
    return navigateTo(destination, { replace: true })
  }
  return navigateTo(destination)
})
