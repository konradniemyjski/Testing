<template>
  <div class="container">
    <div class="card">
      <h1>Utwórz konto</h1>
      <p class="text-muted">Dołącz do zespołu i rejestruj czas pracy brygady.</p>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="email">Adres e-mail</label>
          <input id="email" v-model="form.email" type="email" required placeholder="twoj@przyklad.pl" />
        </div>

        <div class="form-group">
          <label for="fullName">Imię i nazwisko</label>
          <input id="fullName" v-model="form.full_name" type="text" placeholder="Jan Kowalski" />
        </div>

        <div class="form-group">
          <label for="password">Hasło</label>
          <input id="password" v-model="form.password" type="password" required placeholder="********" />
        </div>

        <div class="form-group">
          <label for="role">Rola</label>
          <select id="role" v-model="form.role">
            <option value="user">Użytkownik</option>
            <option value="admin">Administrator</option>
          </select>
        </div>

        <button class="primary-btn" type="submit" :disabled="loading">
          {{ loading ? 'Tworzenie konta…' : 'Utwórz konto' }}
        </button>
      </form>

      <p class="text-muted" style="margin-top: 1.5rem;">
        Masz już konto?
        <NuxtLink to="/login">Zaloguj się</NuxtLink>
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
    error.value = 'Adres e-mail i hasło są wymagane.'
    return
  }

  try {
    loading.value = true
    error.value = ''
    success.value = ''
    await register({ ...form })
    success.value = 'Konto zostało utworzone! Możesz się teraz zalogować.'
    setTimeout(() => router.push('/login'), 600)
  } catch (err: any) {
    error.value = 'Nie udało się utworzyć konta. Spróbuj ponownie.'
  } finally {
    loading.value = false
  }
}
</script>
