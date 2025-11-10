<template>
  <div class="container">
    <MainNavigation :can-manage-users="canManageUsers" @logout="handleLogout" />
    <div class="card">
      <header style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
        <div>
          <h1>Panel główny</h1>
          <p class="text-muted">
            Witaj ponownie, {{ userStore.profile?.full_name || userStore.profile?.email }}.
          </p>
        </div>
        <p class="badge">Rola: {{ roleLabel }}</p>
      </header>

      <section style="margin-top: 2rem; display: grid; gap: 2rem;">
        <div>
          <h2>Zarejestruj godziny</h2>
          <form @submit.prevent="handleCreate" style="display: grid; gap: 1rem;">
            <div class="form-group">
              <label for="project">Budowa</label>
              <select id="project" v-model.number="form.project_id" required>
                <option disabled value="">Wybierz budowę</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }} ({{ project.code }})
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="date">Data</label>
              <input id="date" v-model="form.date" type="date" required />
            </div>
            <div class="form-group">
              <label for="siteCode">Kod budowy</label>
              <input id="siteCode" v-model="form.site_code" type="text" required />
            </div>
            <div class="form-group">
              <label for="employeeCount">Liczba pracowników</label>
              <input
                id="employeeCount"
                v-model.number="form.employee_count"
                type="number"
                min="1"
                max="1000"
                required
              />
            </div>
            <div class="form-group">
              <label for="hoursWorked">Łączna liczba godzin</label>
              <input
                id="hoursWorked"
                v-model.number="form.hours_worked"
                type="number"
                min="0.25"
                max="2000"
                step="0.25"
                required
              />
            </div>
            <div class="form-group">
              <label for="mealsServed">Posiłki wydane</label>
              <input
                id="mealsServed"
                v-model.number="form.meals_served"
                type="number"
                min="0"
                max="2000"
              />
            </div>
            <div class="form-group">
              <label for="overnightStays">Noclegi</label>
              <input
                id="overnightStays"
                v-model.number="form.overnight_stays"
                type="number"
                min="0"
                max="2000"
              />
            </div>
            <div class="form-group">
              <label for="absences">Nieobecności (dniówki)</label>
              <input
                id="absences"
                v-model.number="form.absences"
                type="number"
                min="0"
                max="2000"
              />
            </div>
            <div class="form-group">
              <label for="notes">Uwagi</label>
              <textarea
                id="notes"
                v-model="form.notes"
                rows="3"
                placeholder="Dodatkowe informacje dla działu księgowości"
              ></textarea>
            </div>
            <button class="primary-btn" type="submit" :disabled="saving">
              {{ saving ? 'Zapisywanie…' : 'Zapisz wpis' }}
            </button>
          </form>
        </div>

        <div>
          <header style="display: flex; justify-content: space-between; align-items: center; gap: 0.75rem;">
            <h2>Ostatnie wpisy</h2>
            <button
              class="primary-btn"
              type="button"
              @click="exportWorklogs"
              :disabled="exporting || !worklogs.length"
            >
              {{ exporting ? 'Przygotowywanie…' : 'Eksportuj do XLSX' }}
            </button>
          </header>

          <table v-if="worklogs.length" class="table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Kod budowy</th>
                <th>Budowa</th>
                <th>Pracownicy</th>
                <th>Łączna liczba godzin</th>
                <th>Posiłki</th>
                <th>Noclegi</th>
                <th>Nieobecności</th>
                <th>Uwagi</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in worklogs" :key="entry.id">
                <td>{{ formatDate(entry.date) }}</td>
                <td>{{ entry.site_code }}</td>
                <td>{{ findProject(entry.project_id)?.name || '—' }}</td>
                <td>{{ entry.employee_count }}</td>
                <td>{{ formatNumber(entry.hours_worked) }}</td>
                <td>{{ entry.meals_served }}</td>
                <td>{{ entry.overnight_stays }}</td>
                <td>{{ entry.absences }}</td>
                <td>{{ entry.notes || '—' }}</td>
                <td>
                  <button
                    type="button"
                    class="primary-btn"
                    style="padding: 0.35rem 1rem;"
                    @click="handleDelete(entry.id)"
                  >
                    Usuń
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">Brak wpisów. Dodaj pierwszy wpis powyżej!</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useUserStore } from '~/stores/user'

type Project = {
  id: number
  code: string
  name: string
  description?: string | null
}

type WorkLog = {
  id: number
  project_id: number
  date: string
  site_code: string
  employee_count: number
  hours_worked: number
  meals_served: number
  overnight_stays: number
  absences: number
  notes?: string | null
}

const router = useRouter()
const userStore = useUserStore()
const api = useApi()

const projects = ref<Project[]>([])
const worklogs = ref<WorkLog[]>([])
const saving = ref(false)
const exporting = ref(false)
const form = reactive({
  project_id: null as number | null,
  date: new Date().toISOString().slice(0, 10),
  site_code: '',
  employee_count: 1,
  hours_worked: 8,
  meals_served: 0,
  overnight_stays: 0,
  absences: 0,
  notes: ''
})

const roleLabel = computed(() => {
  if (userStore.profile?.role === 'admin') {
    return 'Administrator'
  }
  return 'Użytkownik'
})

const canManageUsers = computed(() => userStore.profile?.role === 'admin')

function findProject(id: number | null | undefined) {
  if (id == null) {
    return undefined
  }
  return projects.value.find((project) => project.id === id)
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('pl-PL')
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 2 }).format(value)
}

async function loadProjects() {
  projects.value = await api<Project[]>('/projects/')
  if (!form.project_id && projects.value.length) {
    form.project_id = projects.value[0].id
    form.site_code = projects.value[0].code
  }
}

async function loadWorklogs() {
  worklogs.value = await api<WorkLog[]>('/worklogs/')
}

watch(
  () => form.project_id,
  (newId) => {
    const project = findProject(newId ?? undefined)
    if (project) {
      form.site_code = project.code
    }
  }
)

async function handleCreate() {
  if (!form.project_id) return
  try {
    saving.value = true
    const trimmedSiteCode = form.site_code.trim()
    const payload = {
      ...form,
      site_code: trimmedSiteCode,
      date: new Date(form.date).toISOString(),
      notes: form.notes.trim() ? form.notes.trim() : null
    }
    form.site_code = trimmedSiteCode
    await api<WorkLog>('/worklogs/', {
      method: 'POST',
      body: payload
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

async function exportWorklogs() {
  if (!worklogs.value.length) return
  try {
    exporting.value = true
    const blob = await api<Blob>('/worklogs/export', {
      responseType: 'blob' as const
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `raport_godzin_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    window.alert('Nie udało się pobrać raportu. Spróbuj ponownie.')
  } finally {
    exporting.value = false
  }
}

async function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

onMounted(async () => {
  userStore.hydrateFromStorage()
  if (!userStore.isAuthenticated) {
    router.replace('/login')
    return
  }
  await Promise.all([loadProjects(), loadWorklogs()])
})
</script>
