<template>
  <div class="container">
    <MainNavigation @logout="handleLogout" />
    
    <div class="card profile-card">
      <header>
        <h1>Twój Profil</h1>
        <p class="text-muted">Zarządzaj swoimi danymi i ustawieniami konta.</p>
      </header>
      
      <div class="profile-grid">
        <!-- Personal Details Section -->
        <section class="profile-section">
          <h2>Dane podstawowe</h2>
          <form @submit.prevent="updateDetails" class="profile-form">
            <div class="form-group">
              <label for="fullName">Imię i nazwisko</label>
              <input 
                id="fullName" 
                v-model="detailsForm.full_name" 
                type="text" 
                placeholder="Np. Jan Kowalski"
              />
            </div>
            
            <div class="form-group">
              <label for="email">Adres email</label>
              <input 
                id="email" 
                v-model="detailsForm.email" 
                type="email" 
                required
              />
            </div>
            
            <div class="actions">
              <p v-if="detailsSuccess" class="success-msg">{{ detailsSuccess }}</p>
              <p v-if="detailsError" class="error-msg">{{ detailsError }}</p>
              <button class="primary-btn" type="submit" :disabled="detailsLoading">
                {{ detailsLoading ? 'Zapisywanie...' : 'Zaktualizuj dane' }}
              </button>
            </div>
          </form>
        </section>

        <!-- Security Section -->
        <section class="profile-section">
          <h2>Zmiana hasła</h2>
          <form @submit.prevent="updatePassword" class="profile-form">
            <div class="form-group">
              <label for="currentPassword">Obecne hasło</label>
              <input 
                id="currentPassword" 
                v-model="passwordForm.current_password" 
                type="password" 
                required
                autocomplete="current-password"
              />
            </div>
            
            <div class="form-group">
              <label for="newPassword">Nowe hasło</label>
              <input 
                id="newPassword" 
                v-model="passwordForm.new_password" 
                type="password" 
                required
                minlength="6"
                autocomplete="new-password"
              />
              <small class="text-muted">Minimum 6 znaków</small>
            </div>

             <div class="form-group">
              <label for="confirmPassword">Powtórz nowe hasło</label>
              <input 
                id="confirmPassword" 
                v-model="passwordForm.confirm_password" 
                type="password" 
                required
                minlength="6"
                autocomplete="new-password"
              />
            </div>
            
            <div class="actions">
              <p v-if="passwordSuccess" class="success-msg">{{ passwordSuccess }}</p>
              <p v-if="passwordError" class="error-msg">{{ passwordError }}</p>
              <button class="primary-btn warning-btn" type="submit" :disabled="passwordLoading">
                {{ passwordLoading ? 'Zmienianie...' : 'Zmień hasło' }}
              </button>
            </div>
          </form>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useApi } from '~/composables/useApi'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

const router = useRouter()
const userStore = useUserStore()
const api = useApi()

// Details Form
const detailsForm = reactive({
  full_name: '',
  email: ''
})
const detailsLoading = ref(false)
const detailsSuccess = ref('')
const detailsError = ref('')

// Password Form
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordLoading = ref(false)
const passwordSuccess = ref('')
const passwordError = ref('')

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

// Hydrate form with user data
onMounted(async () => {
  userStore.hydrateFromStorage()
  if (!userStore.isAuthenticated) {
    router.replace('/login')
    return
  }
  
  if (userStore.profile) {
    detailsForm.full_name = userStore.profile.full_name || ''
    detailsForm.email = userStore.profile.email
  }
})

async function updateDetails() {
  detailsLoading.value = true
  detailsSuccess.value = ''
  detailsError.value = ''
  
  try {
    const payload = {
      full_name: detailsForm.full_name,
      email: detailsForm.email
    }
    
    const updatedUser = await api('/auth/me', {
      method: 'PUT',
      body: payload
    })
    
    // Update store
    userStore.setProfile(updatedUser)
    detailsSuccess.value = 'Dane zostały zaktualizowane.'
  } catch (error: any) {
    detailsError.value = error.data?.detail || 'Nie udało się zaktualizować danych.'
  } finally {
    detailsLoading.value = false
  }
}

async function updatePassword() {
  passwordLoading.value = true
  passwordSuccess.value = ''
  passwordError.value = ''

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = 'Hasła nie są identyczne.'
    passwordLoading.value = false
    return
  }

  if (passwordForm.new_password.length < 6) {
    passwordError.value = 'Hasło musi mieć co najmniej 6 znaków.'
    passwordLoading.value = false
    return
  }

  try {
    const payload = {
      current_password: passwordForm.current_password,
      password: passwordForm.new_password
    }

    await api('/auth/me', {
      method: 'PUT',
      body: payload
    })

    passwordSuccess.value = 'Hasło zostało zmienione.'
    // Reset form
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error: any) {
    passwordError.value = error.data?.detail || 'Nie udało się zmienić hasła (sprawdź obecne hasło).'
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style scoped>
.profile-card {
  max-width: 900px;
  margin: 0 auto;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
  margin-top: 2rem;
}

@media (min-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.profile-section h2 {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  color: #1f2937;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.profile-form {
  display: grid;
  gap: 1.25rem;
}

.actions {
  margin-top: 1rem;
}

.warning-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}
.warning-btn:hover {
  box-shadow: 0 10px 20px rgba(245, 158, 11, 0.3);
}

.success-msg {
  color: #10b981;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.error-msg {
  color: #ef4444;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

@media (prefers-color-scheme: dark) {
  .profile-section h2 {
    color: #f3f4f6;
    border-color: #374151;
  }
}
</style>
