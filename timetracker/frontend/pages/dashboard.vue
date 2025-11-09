<template>
  <div class="container">
    <div class="card">
      <header style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
        <div>
          <h1>Dashboard</h1>
          <p class="text-muted">Welcome back, {{ userStore.profile?.full_name || userStore.profile?.email }}.</p>
        </div>
        <div style="text-align: right;">
          <p class="badge">Role: {{ userStore.profile?.role }}</p>
          <button class="primary-btn" style="margin-top: 0.5rem;" @click="handleLogout">Sign out</button>
        </div>
      </header>

      <section style="margin-top: 2rem; display: grid; gap: 2rem;">
        <div>
          <h2>Log hours</h2>
          <form @submit.prevent="handleCreate">
            <div class="form-group">
              <label for="project">Project</label>
              <select id="project" v-model.number="form.project_id" required>
                <option disabled value="">Select a project</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="date">Date</label>
              <input id="date" v-model="form.date" type="date" required />
            </div>
            <div class="form-group">
              <label for="hours">Hours</label>
              <input id="hours" v-model.number="form.hours" type="number" min="1" max="24" required />
            </div>
            <div class="form-group">
              <label for="notes">Notes</label>
              <textarea id="notes" v-model="form.notes" rows="3" placeholder="What did you work on?"></textarea>
            </div>
            <button class="primary-btn" type="submit" :disabled="saving">
              {{ saving ? 'Saving…' : 'Save entry' }}
            </button>
          </form>
        </div>

        <div>
          <header style="display: flex; justify-content: space-between; align-items: center;">
            <h2>Recent work logs</h2>
            <div v-if="userStore.profile?.role === 'admin'">
              <button class="primary-btn" type="button" @click="showProjectModal = true">New project</button>
            </div>
          </header>

          <table v-if="worklogs.length" class="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Project</th>
                <th>Hours</th>
                <th>Notes</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in worklogs" :key="entry.id">
                <td>{{ formatDate(entry.date) }}</td>
                <td>{{ findProject(entry.project_id)?.name || 'Unknown' }}</td>
                <td>{{ entry.hours }}</td>
                <td>{{ entry.notes || '—' }}</td>
                <td>
                  <button type="button" class="primary-btn" style="padding: 0.35rem 1rem;" @click="handleDelete(entry.id)">
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">No entries yet. Log your first hour above!</p>
        </div>
      </section>
    </div>

    <dialog ref="projectDialog" @close="showProjectModal = false">
      <form class="card" method="dialog" @submit.prevent="createProject">
        <h2>Create project</h2>
        <div class="form-group">
          <label for="projectName">Name</label>
          <input id="projectName" v-model="projectForm.name" type="text" required />
        </div>
        <div class="form-group">
          <label for="projectDesc">Description</label>
          <textarea id="projectDesc" v-model="projectForm.description" rows="3" />
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 0.75rem;">
          <button type="button" class="primary-btn" style="background: #e11d48;" @click="closeProjectModal">Cancel</button>
          <button type="submit" class="primary-btn">Create</button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useUserStore } from '~/stores/user'

type Project = {
  id: number
  name: string
  description?: string | null
}

type WorkLog = {
  id: number
  project_id: number
  date: string
  hours: number
  notes?: string | null
}

const router = useRouter()
const userStore = useUserStore()
const api = useApi()

const projects = ref<Project[]>([])
const worklogs = ref<WorkLog[]>([])
const saving = ref(false)
const showProjectModal = ref(false)
const projectDialog = ref<HTMLDialogElement | null>(null)

watch(showProjectModal, (open) => {
  if (!projectDialog.value) return
  if (open) projectDialog.value.showModal()
  else projectDialog.value.close()
})

const form = reactive({
  project_id: null as number | null,
  date: new Date().toISOString().slice(0, 10),
  hours: 8,
  notes: ''
})

const projectForm = reactive({
  name: '',
  description: ''
})

function findProject(id: number) {
  return projects.value.find((project) => project.id === id)
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString()
}

async function loadProjects() {
  projects.value = await api<Project[]>('/projects/')
  if (!form.project_id && projects.value.length) {
    form.project_id = projects.value[0].id
  }
}

async function loadWorklogs() {
  worklogs.value = await api<WorkLog[]>('/worklogs/')
}

async function handleCreate() {
  if (!form.project_id) return
  try {
    saving.value = true
    await api<WorkLog>('/worklogs/', {
      method: 'POST',
      body: { ...form, date: new Date(form.date).toISOString() }
    })
    form.notes = ''
    await loadWorklogs()
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  await api(`/worklogs/${id}`, { method: 'DELETE' })
  await loadWorklogs()
}

function closeProjectModal() {
  showProjectModal.value = false
}

async function createProject() {
  if (!projectForm.name.trim()) return
  await api<Project>('/projects/', {
    method: 'POST',
    body: { ...projectForm }
  })
  projectForm.name = ''
  projectForm.description = ''
  showProjectModal.value = false
  await loadProjects()
}

async function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

onMounted(async () => {
  if (!userStore.isAuthenticated) {
    router.replace('/login')
    return
  }
  await Promise.all([loadProjects(), loadWorklogs()])
})
</script>
