<template>
  <div class="container">
    <div class="card">
      <header style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
        <div>
          <h1>Zarządzanie użytkownikami</h1>
          <p class="text-muted">Przeglądaj konta i przypisuj odpowiednie role.</p>
        </div>
        <div style="display: flex; gap: 0.75rem; align-items: center;">
          <button class="primary-btn" type="button" @click="goToDashboard">Panel główny</button>
          <button class="primary-btn" type="button" @click="handleLogout">Wyloguj</button>
        </div>
      </header>

      <section style="margin-top: 2rem; display: grid; gap: 1.5rem;">
        <p class="text-muted">
          Każda nowo zarejestrowana osoba otrzymuje rolę użytkownika. Administrator może tutaj podnieść
          uprawnienia wybranych kont.
        </p>

        <p v-if="errorMessage" style="color: #ef4444;">{{ errorMessage }}</p>
        <p v-if="successMessage" style="color: #10b981;">{{ successMessage }}</p>

        <table v-if="users.length" class="table">
          <thead>
            <tr>
              <th>Login</th>
              <th>Imię i nazwisko</th>
              <th>Rola</th>
              <th>Utworzono</th>
              <th>Ostatnia aktualizacja</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.email }}</td>
              <td>{{ user.full_name || '—' }}</td>
              <td>
                <select
                  :value="user.role"
                  @change="onRoleChange(user.id, $event)"
                  :disabled="updatingUserId === user.id"
                >
                  <option value="user">Użytkownik</option>
                  <option value="admin">Administrator</option>
                </select>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>{{ formatDate(user.updated_at) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">
          {{ loading ? 'Trwa ładowanie użytkowników…' : 'Brak danych do wyświetlenia.' }}
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useApi } from '~/composables/useApi'
import { useUserStore } from '~/stores/user'

type Role = 'user' | 'admin'

type User = {
  id: number
  email: string
  full_name?: string | null
  role: Role
  created_at: string
  updated_at: string
}

const router = useRouter()
const api = useApi()
const userStore = useUserStore()

const users = ref<User[]>([])
const loading = ref(false)
const updatingUserId = ref<number | null>(null)
const errorMessage = ref('')
const successMessage = ref('')

function formatDate(value: string) {
  return new Date(value).toLocaleString('pl-PL')
}

async function loadUsers() {
  loading.value = true
  errorMessage.value = ''
  try {
    users.value = await api<User[]>('/users/')
  } catch (error: any) {
    if (error?.statusCode === 401) {
      userStore.clear()
      router.replace('/login')
      return
    }
    if (error?.statusCode === 403) {
      router.replace('/dashboard')
      return
    }
    errorMessage.value = 'Nie udało się pobrać listy użytkowników.'
  } finally {
    loading.value = false
  }
}

async function updateRole(userId: number, role: Role) {
  updatingUserId.value = userId
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const updatedUser = await api<User>(`/users/${userId}/role`, {
      method: 'PATCH',
      body: { role }
    })
    users.value = users.value.map((user) => (user.id === userId ? updatedUser : user))
    successMessage.value = 'Rola została zaktualizowana.'
  } catch (error: any) {
    if (error?.statusCode === 401) {
      userStore.clear()
      router.replace('/login')
      return
    }
    if (error?.statusCode === 403) {
      router.replace('/dashboard')
      return
    }
    errorMessage.value = 'Nie udało się zaktualizować roli użytkownika.'
  } finally {
    updatingUserId.value = null
  }
}

function onRoleChange(userId: number, event: Event) {
  const select = event.target as HTMLSelectElement
  updateRole(userId, select.value as Role)
}

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

function goToDashboard() {
  router.push('/dashboard')
}

onMounted(async () => {
  userStore.hydrateFromStorage()
  if (!userStore.isAuthenticated) {
    router.replace('/login')
    return
  }

  if (userStore.profile?.role !== 'admin') {
    router.replace('/dashboard')
    return
  }

  await loadUsers()
})
</script>
