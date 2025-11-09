<template>
  <div class="container">
    <div class="card">
      <h1>Create your account</h1>
      <p class="text-muted">Join your team and start logging time.</p>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="form.email" type="email" required placeholder="you@example.com" />
        </div>

        <div class="form-group">
          <label for="fullName">Full name</label>
          <input id="fullName" v-model="form.full_name" type="text" placeholder="Jane Doe" />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input id="password" v-model="form.password" type="password" required placeholder="********" />
        </div>

        <div class="form-group">
          <label for="role">Role</label>
          <select id="role" v-model="form.role">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <button class="primary-btn" type="submit" :disabled="loading">
          {{ loading ? 'Creating account…' : 'Create account' }}
        </button>
      </form>

      <p class="text-muted" style="margin-top: 1.5rem;">
        Already registered?
        <NuxtLink to="/login">Sign in</NuxtLink>
      </p>

      <p v-if="success" style="color: #10b981;">{{ success }}</p>
      <p v-if="error" style="color: #ef4444;">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { register } from '~/stores/user'

const router = useRouter()
const form = reactive({
  email: '',
  password: '',
  full_name: '',
  role: 'user' as 'user' | 'admin'
})
const loading = ref(false)
const success = ref('')
const error = ref('')

async function handleRegister() {
  if (!form.email || !form.password) {
    error.value = 'Email and password are required.'
    return
  }

  try {
    loading.value = true
    error.value = ''
    success.value = ''
    await register({ ...form })
    success.value = 'Account created! You can sign in now.'
    setTimeout(() => router.push('/login'), 600)
  } catch (err: any) {
    error.value = err?.data?.detail ?? 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
