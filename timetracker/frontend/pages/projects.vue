<template>
  <div class="container">
    <div class="card">
      <header style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
        <div>
          <h1>Budowy</h1>
          <p class="text-muted">Twórz i przeglądaj budowy wykorzystywane przy rozliczaniu pracy.</p>
        </div>
        <div style="display: flex; gap: 0.75rem; align-items: center;">
          <button class="primary-btn" type="button" @click="goToDashboard">Panel główny</button>
          <button class="primary-btn" type="button" @click="handleLogout">Wyloguj</button>
        </div>
      </header>

      <section style="margin-top: 2rem; display: grid; gap: 2rem;">
        <div>
          <h2>Dodaj budowę</h2>
          <p class="text-muted">Budowę może dodać każda zalogowana osoba nadzorująca.</p>
          <form @submit.prevent="createProject" style="margin-top: 1rem; display: grid; gap: 1rem;">
            <div class="form-group">
              <label for="projectCode">Kod budowy</label>
              <input id="projectCode" v-model="form.code" type="text" required placeholder="np. BUD-123" />
            </div>
            <div class="form-group">
              <label for="projectName">Nazwa</label>
              <input id="projectName" v-model="form.name" type="text" required placeholder="np. Osiedle Zielone" />
            </div>
            <div class="form-group">
              <label for="projectDescription">Opis</label>
              <textarea
                id="projectDescription"
                v-model="form.description"
                rows="3"
                placeholder="Opcjonalne informacje dla brygadzistów"
              ></textarea>
            </div>
            <p v-if="errorMessage" class="text-muted" style="color: #f87171;">{{ errorMessage }}</p>
            <p v-if="successMessage" class="text-muted" style="color: #34d399;">{{ successMessage }}</p>
            <button class="primary-btn" type="submit" :disabled="saving">
              {{ saving ? 'Zapisywanie…' : 'Dodaj budowę' }}
            </button>
          </form>
        </div>

        <div>
          <h2>Zarejestrowane budowy</h2>
          <table v-if="projects.length" class="table" style="margin-top: 1rem;">
            <thead>
              <tr>
                <th>Kod</th>
                <th>Nazwa</th>
                <th>Opis</th>
                <th>Utworzono</th>
                <th>Zaktualizowano</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="project in projects" :key="project.id">
                <td>{{ project.code }}</td>
                <td>{{ project.name }}</td>
                <td>{{ project.description || '—' }}</td>
                <td>{{ formatDate(project.created_at) }}</td>
                <td>{{ formatDate(project.updated_at) }}</td>
                <td>
                  <div style="display: flex; gap: 0.5rem;">
                    <button 
                      class="btn-edit" 
                      type="button" 
                      @click="openEditModal(project)"
                      title="Edytuj"
                    >
                      ✏️
                    </button>
                    <button 
                      class="btn-delete" 
                      type="button" 
                      @click="openDeleteModal(project)"
                      title="Usuń"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted" style="margin-top: 1rem;">
            {{ loading ? 'Trwa ładowanie budów…' : 'Brak budów. Dodaj pierwszą powyżej.' }}
          </p>
        </div>
      </section>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <h2>Edytuj budowę</h2>
        <form @submit.prevent="updateProject" style="margin-top: 1rem; display: grid; gap: 1rem;">
          <div class="form-group">
            <label for="editProjectCode">Kod budowy</label>
            <input 
              id="editProjectCode" 
              v-model="editForm.code" 
              type="text" 
              required 
              placeholder="np. BUD-123" 
            />
          </div>
          <div class="form-group">
            <label for="editProjectName">Nazwa</label>
            <input 
              id="editProjectName" 
              v-model="editForm.name" 
              type="text" 
              required 
              placeholder="np. Osiedle Zielone" 
            />
          </div>
          <div class="form-group">
            <label for="editProjectDescription">Opis</label>
            <textarea
              id="editProjectDescription"
              v-model="editForm.description"
              rows="3"
              placeholder="Opcjonalne informacje dla brygadzistów"
            ></textarea>
          </div>
          <p v-if="editErrorMessage" class="text-muted" style="color: #f87171;">{{ editErrorMessage }}</p>
          <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
            <button class="secondary-btn" type="button" @click="closeEditModal">
              Anuluj
            </button>
            <button class="primary-btn" type="submit" :disabled="saving">
              {{ saving ? 'Zapisywanie…' : 'Zapisz' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <h2>Potwierdź usunięcie</h2>
        <p v-if="projectToDelete" style="margin: 1.5rem 0;">
          Czy na pewno chcesz usunąć budowę <strong>"{{ projectToDelete.name }}"</strong>?
        </p>
        <p class="text-muted" style="color: #f87171; margin-bottom: 1rem;">
          Ta operacja jest nieodwracalna!
        </p>
        <p v-if="deleteErrorMessage" class="text-muted" style="color: #f87171; margin-bottom: 1rem;">
          {{ deleteErrorMessage }}
        </p>
        <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
          <button class="secondary-btn" type="button" @click="closeDeleteModal">
            Anuluj
          </button>
          <button class="danger-btn" type="button" @click="confirmDelete" :disabled="deleting">
            {{ deleting ? 'Usuwanie…' : 'Usuń' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useApi } from '~/composables/useApi'
import { useUserStore } from '~/stores/user'

const router = useRouter()
const api = useApi()
const userStore = useUserStore()

interface Project {
  id: number
  code: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

const projects = ref<Project[]>([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const editErrorMessage = ref('')
const deleteErrorMessage = ref('')

// Edit modal state
const showEditModal = ref(false)
const editForm = reactive({
  id: 0,
  code: '',
  name: '',
  description: ''
})

// Delete modal state
const showDeleteModal = ref(false)
const projectToDelete = ref<Project | null>(null)

const form = reactive({
  code: '',
  name: '',
  description: ''
})

function formatDate(value: string) {
  return new Date(value).toLocaleString('pl-PL')
}

async function loadProjects() {
  loading.value = true
  try {
    projects.value = await api<Project[]>('/projects/')
  } finally {
    loading.value = false
  }
}

async function createProject() {
  const trimmedCode = form.code.trim()
  const trimmedName = form.name.trim()
  if (!trimmedCode) {
    errorMessage.value = 'Kod budowy jest wymagany.'
    return
  }
  if (!trimmedName) {
    errorMessage.value = 'Nazwa budowy jest wymagana.'
    return
  }

  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const trimmedDescription = form.description.trim()
    const payload = {
      code: trimmedCode,
      name: trimmedName,
      description: trimmedDescription ? trimmedDescription : null
    }
    const project = await api<Project>('/projects/', {
      method: 'POST',
      body: payload
    })
    form.code = ''
    form.name = ''
    form.description = ''
    successMessage.value = 'Budowa została zapisana.'
    projects.value = [project, ...projects.value.filter((item) => item.id !== project.id)]
  } catch (error) {
    errorMessage.value = 'Nie udało się zapisać budowy. Spróbuj ponownie.'
  } finally {
    saving.value = false
  }
}

function openEditModal(project: Project) {
  editForm.id = project.id
  editForm.code = project.code
  editForm.name = project.name
  editForm.description = project.description || ''
  editErrorMessage.value = ''
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  editErrorMessage.value = ''
}

async function updateProject() {
  const trimmedCode = editForm.code.trim()
  const trimmedName = editForm.name.trim()
  
  if (!trimmedCode) {
    editErrorMessage.value = 'Kod budowy jest wymagany.'
    return
  }
  if (!trimmedName) {
    editErrorMessage.value = 'Nazwa budowy jest wymagana.'
    return
  }

  saving.value = true
  editErrorMessage.value = ''

  try {
    const trimmedDescription = editForm.description.trim()
    const payload = {
      code: trimmedCode,
      name: trimmedName,
      description: trimmedDescription ? trimmedDescription : null
    }
    
    const updatedProject = await api<Project>(`/projects/${editForm.id}`, {
      method: 'PUT',
      body: payload
    })
    
    // Update project in the list
    const index = projects.value.findIndex(p => p.id === editForm.id)
    if (index !== -1) {
      projects.value[index] = updatedProject
    }
    
    closeEditModal()
    successMessage.value = 'Budowa została zaktualizowana.'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    editErrorMessage.value = 'Nie udało się zaktualizować budowy. Spróbuj ponownie.'
  } finally {
    saving.value = false
  }
}

function openDeleteModal(project: Project) {
  projectToDelete.value = project
  deleteErrorMessage.value = ''
  showDeleteModal.value = true
}

function closeDeleteModal() {
  showDeleteModal.value = false
  projectToDelete.value = null
  deleteErrorMessage.value = ''
}

async function confirmDelete() {
  if (!projectToDelete.value) return

  deleting.value = true
  deleteErrorMessage.value = ''

  try {
    await api(`/projects/${projectToDelete.value.id}`, {
      method: 'DELETE'
    })
    
    // Remove project from the list
    projects.value = projects.value.filter(p => p.id !== projectToDelete.value!.id)
    
    closeDeleteModal()
    successMessage.value = 'Budowa została usunięta.'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error: any) {
    // Check if error contains information about associated worklogs
    if (error?.data?.detail) {
      deleteErrorMessage.value = error.data.detail
    } else {
      deleteErrorMessage.value = 'Nie udało się usunąć budowy. Spróbuj ponownie.'
    }
  } finally {
    deleting.value = false
  }
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
  await loadProjects()
})
</script>

<style scoped>
.btn-edit {
  padding: 0.25rem 0.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.btn-edit:hover {
  background-color: #2563eb;
}

.btn-delete {
  padding: 0.25rem 0.5rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.btn-delete:hover {
  background-color: #dc2626;
}

.secondary-btn {
  padding: 0.5rem 1rem;
  background-color: #6b7280;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.secondary-btn:hover {
  background-color: #4b5563;
}

.danger-btn {
  padding: 0.5rem 1rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.danger-btn:hover {
  background-color: #dc2626;
}

.danger-btn:disabled,
.secondary-btn:disabled,
.btn-edit:disabled,
.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  min-width: 400px;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-content h2 {
  margin-top: 0;
  color: #333;
}
</style>
