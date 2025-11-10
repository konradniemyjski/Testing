<template>
  <div class="container">
    <MainNavigation @logout="handleLogout" />
    <div class="card">
      <header style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
        <div>
          <h1>Zarządzanie użytkownikami</h1>
          <p class="text-muted">Przeglądaj konta i przypisuj odpowiednie role.</p>
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
              <th>Akcje</th>
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
              <td>
                <div class="icon-actions">
                  <button
                    class="icon-button icon-button--edit"
                    type="button"
                    @click="openEditModal(user)"
                    title="Edytuj użytkownika"
                  >
                    ✏️
                  </button>
                  <button
                    class="icon-button icon-button--delete"
                    type="button"
                    @click="openDeleteModal(user)"
                    title="Usuń użytkownika"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">
          {{ loading ? 'Trwa ładowanie użytkowników…' : 'Brak danych do wyświetlenia.' }}
        </p>
      </section>
    </div>
  </div>

  <!-- Edit user modal -->
  <div v-if="showEditModal" class="modal" @click="closeEditModal">
    <div class="modal-content" @click.stop>
      <h2>Edytuj użytkownika</h2>
      <form @submit.prevent="updateUser" style="margin-top: 1.5rem; display: grid; gap: 1rem;">
        <div class="form-group">
          <label for="editUserEmail">Login</label>
          <input
            id="editUserEmail"
            v-model="editForm.email"
            type="email"
            required
            placeholder="np. jan.kowalski@example.com"
          />
        </div>
        <div class="form-group">
          <label for="editUserFullName">Imię i nazwisko</label>
          <input
            id="editUserFullName"
            v-model="editForm.full_name"
            type="text"
            placeholder="Opcjonalne"
          />
        </div>
        <p v-if="editErrorMessage" class="text-muted" style="color: #ef4444;">{{ editErrorMessage }}</p>
        <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
          <button class="secondary-btn" type="button" @click="closeEditModal">Anuluj</button>
          <button class="primary-btn" type="submit" :disabled="savingEdit">
            {{ savingEdit ? 'Zapisywanie…' : 'Zapisz' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Delete confirmation modal -->
  <div v-if="showDeleteModal" class="modal" @click="closeDeleteModal">
    <div class="modal-content" @click.stop>
      <h2>Usuń użytkownika</h2>
      <p v-if="userToDelete" style="margin: 1.5rem 0;">
        Czy na pewno chcesz usunąć konto <strong>{{ userToDelete.email }}</strong>?
      </p>
      <p class="text-muted" style="color: #ef4444; margin-bottom: 1rem;">
        Ta operacja jest nieodwracalna.
      </p>
      <p v-if="deleteErrorMessage" class="text-muted" style="color: #ef4444; margin-bottom: 1rem;">
        {{ deleteErrorMessage }}
      </p>
      <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
        <button class="secondary-btn" type="button" @click="closeDeleteModal">Anuluj</button>
        <button class="danger-btn" type="button" @click="confirmDelete" :disabled="deletingUser">
          {{ deletingUser ? 'Usuwanie…' : 'Usuń' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
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
const showEditModal = ref(false)
const editErrorMessage = ref('')
const savingEdit = ref(false)
const showDeleteModal = ref(false)
const deleteErrorMessage = ref('')
const deletingUser = ref(false)
const editForm = reactive({
  id: 0,
  email: '',
  full_name: ''
})
const userToDelete = ref<User | null>(null)

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

function openEditModal(user: User) {
  editForm.id = user.id
  editForm.email = user.email
  editForm.full_name = user.full_name ?? ''
  editErrorMessage.value = ''
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  editErrorMessage.value = ''
}

async function updateUser() {
  const trimmedEmail = editForm.email.trim()
  if (!trimmedEmail) {
    editErrorMessage.value = 'Login jest wymagany.'
    return
  }

  savingEdit.value = true
  editErrorMessage.value = ''
  successMessage.value = ''

  try {
    const payload = {
      email: trimmedEmail,
      full_name: editForm.full_name.trim() ? editForm.full_name.trim() : null
    }

    const updatedUser = await api<User>(`/users/${editForm.id}`, {
      method: 'PUT',
      body: payload
    })

    users.value = users.value.map((user) => (user.id === updatedUser.id ? updatedUser : user))

    if (userStore.profile?.id === updatedUser.id) {
      userStore.setCredentials(userStore.accessToken, {
        id: updatedUser.id,
        email: updatedUser.email,
        full_name: updatedUser.full_name,
        role: updatedUser.role
      })
    }

    successMessage.value = 'Dane użytkownika zostały zaktualizowane.'
    closeEditModal()
  } catch (error: any) {
    if (error?.statusCode === 400 && error?.data?.detail) {
      editErrorMessage.value = error.data.detail
    } else {
      editErrorMessage.value = 'Nie udało się zaktualizować użytkownika.'
    }
  } finally {
    savingEdit.value = false
  }
}

function openDeleteModal(user: User) {
  userToDelete.value = user
  deleteErrorMessage.value = ''
  showDeleteModal.value = true
}

function closeDeleteModal() {
  userToDelete.value = null
  deleteErrorMessage.value = ''
  showDeleteModal.value = false
}

async function confirmDelete() {
  if (!userToDelete.value) return

  deletingUser.value = true
  deleteErrorMessage.value = ''
  successMessage.value = ''

  try {
    await api(`/users/${userToDelete.value.id}`, {
      method: 'DELETE'
    })

    users.value = users.value.filter((user) => user.id !== userToDelete.value!.id)
    successMessage.value = 'Użytkownik został usunięty.'
    closeDeleteModal()
  } catch (error: any) {
    if (error?.statusCode === 400 && error?.data?.detail) {
      deleteErrorMessage.value = error.data.detail
    } else {
      deleteErrorMessage.value = 'Nie udało się usunąć użytkownika.'
    }
  } finally {
    deletingUser.value = false
  }
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

<style scoped>
.secondary-btn,
.danger-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 999px;
  color: #ffffff;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.secondary-btn {
  background: #6b7280;
}

.secondary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(107, 114, 128, 0.35);
}

.danger-btn {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.danger-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(239, 68, 68, 0.4);
}

.danger-btn:disabled,
.secondary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.modal {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.6);
  padding: 1.5rem;
  z-index: 1000;
}

.modal-content {
  background: linear-gradient(145deg, #f8fafc, #eef2ff);
  border-radius: 20px;
  padding: 2rem;
  width: min(480px, 100%);
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.15);
}

.modal-content h2 {
  margin-top: 0;
}

@media (prefers-color-scheme: dark) {
  .modal-content {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(51, 65, 85, 0.95));
    color: #f8fafc;
  }
}
</style>
