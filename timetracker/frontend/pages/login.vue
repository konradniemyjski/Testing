<template>
  <div class="container">
    <div class="card">
      <h1>Sign in to Worklog</h1>
      <p class="text-muted">Track your hours with a refreshed Nuxt + FastAPI stack.</p>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="form.email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input id="password" v-model="form.password" type="password" placeholder="********" required />
        </div>
        <button class="primary-btn" type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <p class="text-muted" style="margin-top: 1.5rem;">
        Need an account?
        <NuxtLink to="/register">Create one</NuxtLink>
      </p>

      <p v-if="error" style="color: #ef4444;">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { login, useUserStore } from '~/stores/user'

const router = useRouter()
const userStore = useUserStore()
const form = reactive({
  email: '',
  password: ''
})
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!form.email || !form.password) {
    error.value = 'Email and password are required.'
    return
  }

  try {
    loading.value = true
    error.value = ''
    await login(form.email, form.password)
    router.push('/dashboard')
  } catch (err: any) {
    error.value = err?.data?.detail ?? 'Failed to sign in. Please verify your credentials.'
  } finally {
    loading.value = false
  }
}

if (userStore.isAuthenticated) {
  router.replace('/dashboard')
}
</script>
