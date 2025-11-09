<template>
  <div class="container">
    <div class="card">
      <header style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
        <div>
          <h1>Projects</h1>
          <p class="text-muted">Create and review projects available for work log entries.</p>
        </div>
        <div style="display: flex; gap: 0.75rem; align-items: center;">
          <button class="primary-btn" type="button" @click="goToDashboard">Dashboard</button>
          <button class="primary-btn" type="button" @click="handleLogout">Sign out</button>
        </div>
      </header>

      <section style="margin-top: 2rem; display: grid; gap: 2rem;">
        <div>
          <h2>Add a project</h2>
          <p class="text-muted">Projects can be created by any authenticated user.</p>
          <form @submit.prevent="createProject" style="margin-top: 1rem; display: grid; gap: 1rem;">
            <div class="form-group">
              <label for="projectName">Name</label>
              <input id="projectName" v-model="form.name" type="text" required placeholder="e.g. Marketing website" />
            </div>
            <div class="form-group">
              <label for="projectDescription">Description</label>
              <textarea
                id="projectDescription"
                v-model="form.description"
                rows="3"
                placeholder="Optional context for the team"
              ></textarea>
            </div>
            <p v-if="errorMessage" class="text-muted" style="color: #f87171;">{{ errorMessage }}</p>
            <p v-if="successMessage" class="text-muted" style="color: #34d399;">{{ successMessage }}</p>
            <button class="primary-btn" type="submit" :disabled="saving">
              {{ saving ? 'Creating…' : 'Create project' }}
            </button>
          </form>
        </div>

        <div>
          <h2>Existing projects</h2>
          <table v-if="projects.length" class="table" style="margin-top: 1rem;">
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Created</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="project in projects" :key="project.id">
                <td>{{ project.name }}</td>
                <td>{{ project.description || '—' }}</td>
                <td>{{ formatDate(project.created_at) }}</td>
                <td>{{ formatDate(project.updated_at) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted" style="margin-top: 1rem;">
            {{ loading ? 'Loading projects…' : 'No projects yet. Create one above to get started.' }}
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FetchError } from 'ofetch'
import { useApi } from '~/composables/useApi'
import { useUserStore } from '~/stores/user'

const router = useRouter()
const api = useApi()
const userStore = useUserStore()

interface Project {
  id: number
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
  name: '',
  description: ''
})

function formatDate(value: string) {
  return new Date(value).toLocaleString()
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
  const trimmedName = form.name.trim()
  if (!trimmedName) {
    errorMessage.value = 'Project name is required.'
    return
  }

  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const payload = {
      name: trimmedName,
      description: form.description.trim() ? form.description : null
    }
    const project = await api<Project>('/projects/', {
      method: 'POST',
      body: payload
    })
    form.name = ''
    form.description = ''
    successMessage.value = 'Project created successfully.'
    projects.value = [project, ...projects.value.filter((item) => item.id !== project.id)]
  } catch (error) {
    const fetchError = error as FetchError<{ detail?: string }>
    if (fetchError?.data?.detail) {
      errorMessage.value = fetchError.data.detail
    } else {
      errorMessage.value = 'Unable to create project. Please try again.'
    }
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
