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
              </tr>
            </thead>
            <tbody>
              <tr v-for="project in projects" :key="project.id">
                <td>{{ project.code }}</td>
                <td>{{ project.name }}</td>
                <td>{{ project.description || '—' }}</td>
                <td>{{ formatDate(project.created_at) }}</td>
                <td>{{ formatDate(project.updated_at) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted" style="margin-top: 1rem;">
            {{ loading ? 'Trwa ładowanie budów…' : 'Brak budów. Dodaj pierwszą powyżej.' }}
          </p>
        </div>
      </section>
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
const errorMessage = ref('')
const successMessage = ref('')

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

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

function goToDashboard() {
  router.push('/dashboard')
}

onMounted(async () => {
  if (!userStore.isAuthenticated) {
    router.replace('/login')
    return
  }
  await loadProjects()
})
</script>
