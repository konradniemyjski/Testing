<template>
  <div v-if="ready" class="container">
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
              <label for="teamMember">Zespół</label>
              <select
                id="teamMember"
                v-model.number="form.team_member_id"
                :disabled="!teamMembers.length"
                required
              >
                <option v-if="!teamMembers.length" disabled value="">Brak danych w słowniku</option>
                <option v-for="member in teamMembers" :key="member.id" :value="member.id">
                  {{ member.name }}
                </option>
              </select>
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
              <label for="cateringCompany">Firma cateringowa</label>
              <select
                id="cateringCompany"
                v-model.number="form.catering_company_id"
                :disabled="!cateringCompanies.length"
              >
                <option v-if="!cateringCompanies.length" disabled value="">Brak danych w słowniku</option>
                <option v-for="company in cateringCompanies" :key="company.id" :value="company.id">
                  {{ company.name }} ({{ company.taxId }})
                </option>
              </select>
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
              <label for="accommodationCompany">Firma noclegowa</label>
              <select
                id="accommodationCompany"
                v-model.number="form.accommodation_company_id"
                :disabled="!accommodationCompanies.length"
              >
                <option v-if="!accommodationCompanies.length" disabled value="">Brak danych w słowniku</option>
                <option v-for="company in accommodationCompanies" :key="company.id" :value="company.id">
                  {{ company.name }} ({{ company.taxId }})
                </option>
              </select>
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
                <th>Zespół</th>
                <th>Firma cateringowa</th>
                <th>Firma noclegowa</th>
                <th>Pracownicy</th>
                <th>Łączna liczba godzin</th>
                <th>Posiłki</th>
                <th>Noclegi</th>
                <th>Nieobecności</th>
                <th>Uwagi</th>
                <th v-if="isAdmin">Autor</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in worklogs" :key="entry.id">
                <td>{{ formatDate(entry.date) }}</td>
                <td>{{ entry.site_code }}</td>
                <td>{{ findProject(entry.project_id)?.name || '—' }}</td>
                <td>{{ formatTeam(entry) }}</td>
                <td>{{ formatCatering(entry) }}</td>
                <td>{{ formatAccommodation(entry) }}</td>
                <td>{{ entry.employee_count }}</td>
                <td>{{ formatNumber(entry.hours_worked) }}</td>
                <td>{{ entry.meals_served }}</td>
                <td>{{ entry.overnight_stays }}</td>
                <td>{{ entry.absences }}</td>
                <td>{{ entry.notes || '—' }}</td>
                <td v-if="isAdmin">
                  <span class="author-pill">{{ formatAuthor(entry) }}</span>
                </td>
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
import { useDictionaryStore, type AccommodationCompany, type CateringCompany, type TeamMember } from '~/stores/dictionaries'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

type Project = {
  id: number
  code: string
  name: string
  description?: string | null
}

type WorkLogUser = {
  id: number
  email: string
  full_name?: string | null
}

type WorkLog = {
  id: number
  project_id: number
  team_member_id?: number | null
  accommodation_company_id?: number | null
  catering_company_id?: number | null
  date: string
  site_code: string
  employee_count: number
  hours_worked: number
  meals_served: number
  overnight_stays: number
  absences: number
  user_id: number
  notes?: string | null
  user?: WorkLogUser | null
  team_member?: TeamMember | null
  accommodation_company?: AccommodationCompany | null
  catering_company?: CateringCompany | null
}

const router = useRouter()
const userStore = useUserStore()
const dictionaryStore = useDictionaryStore()
const api = useApi()

const projects = ref<Project[]>([])
const worklogs = ref<WorkLog[]>([])
const saving = ref(false)
const exporting = ref(false)
const ready = ref(false)
const form = reactive({
  project_id: null as number | null,
  date: new Date().toISOString().slice(0, 10),
  site_code: '',
  employee_count: 1,
  hours_worked: 8,
  meals_served: 0,
  overnight_stays: 0,
  absences: 0,
  team_member_id: null as number | null,
  accommodation_company_id: null as number | null,
  catering_company_id: null as number | null,
  notes: ''
})

const isAdmin = computed(() => userStore.profile?.role === 'admin')

const roleLabel = computed(() => {
  if (userStore.profile?.role === 'admin') {
    return 'Administrator'
  }
  return 'Użytkownik'
})

const teamMembers = computed(() => dictionaryStore.teamMembers)
const accommodationCompanies = computed(() => dictionaryStore.accommodationCompanies)
const cateringCompanies = computed(() => dictionaryStore.cateringCompanies)

function findProject(id: number | null | undefined) {
  if (id == null) {
    return undefined
  }
  return projects.value.find((project) => project.id === id)
}

function findTeamMember(id: number | null | undefined) {
  if (id == null) return undefined
  return teamMembers.value.find((member) => member.id === id)
}

function findAccommodationCompany(id: number | null | undefined) {
  if (id == null) return undefined
  return accommodationCompanies.value.find((company) => company.id === id)
}

function findCateringCompany(id: number | null | undefined) {
  if (id == null) return undefined
  return cateringCompanies.value.find((company) => company.id === id)
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('pl-PL')
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 2 }).format(value)
}

function formatAuthor(entry: WorkLog) {
  const author = entry.user
  const displayName = author?.full_name?.trim() || author?.email || 'Nieznany użytkownik'
  const id = author?.id ?? entry.user_id
  return `${displayName} (ID: ${id})`
}

function formatTeam(entry: WorkLog) {
  return entry.team_member?.name || findTeamMember(entry.team_member_id)?.name || '—'
}

function formatCatering(entry: WorkLog) {
  return entry.catering_company?.name || findCateringCompany(entry.catering_company_id)?.name || '—'
}

function formatAccommodation(entry: WorkLog) {
  return (
    entry.accommodation_company?.name ||
    findAccommodationCompany(entry.accommodation_company_id)?.name ||
    '—'
  )
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

watch(
  teamMembers,
  (members) => {
    if (!form.team_member_id && members.length) {
      form.team_member_id = members[0].id
    }
  },
  { immediate: true }
)

watch(
  accommodationCompanies,
  (companies) => {
    if (!form.accommodation_company_id && companies.length) {
      form.accommodation_company_id = companies[0].id
    }
  },
  { immediate: true }
)

watch(
  cateringCompanies,
  (companies) => {
    if (!form.catering_company_id && companies.length) {
      form.catering_company_id = companies[0].id
    }
  },
  { immediate: true }
)

async function handleCreate() {
  if (!form.project_id) return
  try {
    saving.value = true
    const trimmedSiteCode = form.site_code.trim()
    const userNotes = form.notes.trim()
    const payload = {
      ...form,
      site_code: trimmedSiteCode || findProject(form.project_id)?.code || '',
      date: new Date(form.date).toISOString(),
      notes: userNotes || null
    }
    form.site_code = trimmedSiteCode || findProject(form.project_id)?.code || ''
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
  await dictionaryStore.fetchDictionaries()
  await Promise.all([loadProjects(), loadWorklogs()])
  ready.value = true
})
</script>

<style scoped>
.author-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
  font-weight: 600;
  font-size: 0.85rem;
}

@media (prefers-color-scheme: dark) {
  .author-pill {
    background: rgba(59, 130, 246, 0.25);
    color: #bfdbfe;
  }
}
</style>
