<template>
  <div class="container">
    <div class="card">
      <h1>Zaloguj się do rejestru pracy</h1>
      <p class="text-muted">Monitoruj godziny pracy brygady na placach budowy.</p>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Adres e-mail</label>
          <input id="email" v-model="form.email" type="email" placeholder="twoj@przyklad.pl" required />
        </div>
        <div class="form-group">
          <label for="password">Hasło</label>
          <input id="password" v-model="form.password" type="password" placeholder="********" required />
        </div>
        <button class="primary-btn" type="submit" :disabled="loading">
          {{ loading ? 'Trwa logowanie…' : 'Zaloguj się' }}
        </button>
      </form>

      <p class="text-muted" style="margin-top: 1.5rem;">
        Nie masz konta?
        <NuxtLink to="/register">Utwórz je</NuxtLink>
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
    error.value = 'Adres e-mail i hasło są wymagane.'
    return
  }

  try {
    loading.value = true
    error.value = ''
    await login(form.email, form.password)
    router.push('/dashboard')
  } catch (err: any) {
    error.value = 'Nie udało się zalogować. Sprawdź dane i spróbuj ponownie.'
  } finally {
    loading.value = false
  }
}

if (userStore.isAuthenticated) {
  router.replace('/dashboard')
}
</script>
