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
          <form @submit.prevent="handleCreate" class="registration-form">
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
              <label for="teamSelect">Zespół</label>
              <select
                id="teamSelect"
                v-model.number="selectedTeamId"
                :disabled="!teams.length"
                required
              >
                <option v-if="!teams.length" disabled value="">Brak danych w słowniku</option>
                <option v-for="team in teams" :key="team.id" :value="team.id">
                  {{ team.name || 'Bez nazwy' }}
                </option>
              </select>
            </div>

            <!-- Bulk Entry Section -->
            <div v-if="selectedTeamId" class="bulk-entry-section">
              <h3>Członkowie zespołu ({{ filteredTeamMembers.length }})</h3>
              
              <div v-for="(entry, index) in entries" :key="entry.team_member_id" class="member-card">
                <div class="member-header">
                  <strong>{{ findTeamMember(entry.team_member_id)?.name }}</strong>
                  <div class="attendance-toggle">
                    <label>
                      <input type="checkbox" v-model="entry.isPresent"> Obecny
                    </label>
                  </div>
                </div>

                <div v-if="entry.isPresent" class="member-details">
                  <div class="form-group-inline">
                    <label>Godz.</label>
                    <input type="number" v-model.number="entry.hours_worked" min="0.25" step="0.25" style="width: 80px">
                  </div>
                  <div class="form-group-inline">
                    <label>Posiłki</label>
                    <input type="number" v-model.number="entry.meals_served" min="0" style="width: 60px">
                  </div>
                  <div class="form-group-inline">
                    <label>Nocleg</label>
                    <input type="number" v-model.number="entry.overnight_stays" min="0" style="width: 60px">
                  </div>
                </div>

                <div v-else class="member-absence">
                  <select v-model="entry.absenceReason" class="absence-select">
                    <option value="Urlop">Urlop</option>
                    <option value="L4">L4</option>
                    <option value="Inne">Inne</option>
                    <option value="Nieusprawiedliwiona">Nieusprawiedliwiona</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Common Fields for Bulk -->
            <div class="form-group">
              <label for="cateringCompany">Firma cateringowa</label>
              <select
                id="cateringCompany"
                v-model.number="form.catering_company_id"
                :disabled="!cateringCompanies.length"
              >
                <option v-if="!cateringCompanies.length" disabled value="">Brak danych w słowniku</option>
                <option v-for="company in cateringCompanies" :key="company.id" :value="company.id">
                  {{ company.name }} ({{ company.tax_id }})
                </option>
              </select>
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
                  {{ company.name }} ({{ company.tax_id }})
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="notes">Uwagi do całej ekipy</label>
              <textarea
                id="notes"
                v-model="form.notes"
                rows="3"
                placeholder="Dodatkowe informacje dla działu księgowości"
              ></textarea>
            </div>

            <div>
              <button class="primary-btn" type="submit" :disabled="saving">
                {{ saving ? 'Zapisywanie…' : 'Zapisz wpisy' }}
              </button>
            </div>
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
import { storeToRefs } from 'pinia'
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

type BatchEntry = {
  team_member_id: number
  isPresent: boolean
  hours_worked: number
  meals_served: number
  overnight_stays: number
  absenceReason: string
}

const entries = ref<BatchEntry[]>([])

const form = reactive({
  project_id: null as number | null,
  date: new Date().toISOString().slice(0, 10),
  site_code: '',
  catering_company_id: null as number | null,
  accommodation_company_id: null as number | null,
  notes: ''
})

const isAdmin = computed(() => userStore.profile?.role === 'admin')

const roleLabel = computed(() => {
  if (userStore.profile?.role === 'admin') {
    return 'Administrator'
  }
  return 'Użytkownik'
})

const { teams, teamMembers, accommodationCompanies, cateringCompanies } = storeToRefs(dictionaryStore)

const selectedTeamId = ref<number | null>(null)
const filteredTeamMembers = computed(() => {
  if (selectedTeamId.value == null) {
    return teamMembers.value
  }
  return teamMembers.value.filter((member) => member.team_id === selectedTeamId.value)
})

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

function findTeam(id: number | null | undefined) {
  if (id == null) return undefined
  return teams.value.find((team) => team.id === id)
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
  const member = entry.team_member || findTeamMember(entry.team_member_id)
  const memberName = member?.name
  const memberTeam = findTeam(member?.team_id)
  if (!memberName) {
    return '—'
  }
  return memberTeam?.name ? `${memberName} (${memberTeam.name})` : memberName
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
  teams,
  (teamList) => {
    if (teamList.length && selectedTeamId.value == null) {
      selectedTeamId.value = teamList[0].id
    }
  },
  { immediate: true }
)

watch(selectedTeamId, async (newId) => {
  if (!newId) {
    entries.value = []
    return
  }
  
  // 1. Initialize entries for all members
  const members = teamMembers.value.filter(m => m.team_id === newId)
  entries.value = members.map(m => ({
    team_member_id: m.id,
    isPresent: true,
    hours_worked: 8,
    meals_served: 0,
    overnight_stays: 0,
    absenceReason: 'Urlop'
  }))

  // 2. Pre-fill common data from history
  try {
    const lastLog = await api<WorkLog | null>('/worklogs/latest-by-team', {
      params: { team_id: newId }
    })
    
    if (lastLog) {
      form.project_id = lastLog.project_id
      form.site_code = lastLog.site_code
      form.catering_company_id = lastLog.catering_company_id || null
      form.accommodation_company_id = lastLog.accommodation_company_id || null
    }
  } catch (e) {
    console.error('Failed to fetch last worklog for team suggestion', e)
  }
})

// Removed watcher for filteredTeamMembers since we manage 'entries' manually now


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
  if (!form.project_id || !selectedTeamId.value) return
  
  try {
    saving.value = true
    const trimmedSiteCode = form.site_code.trim()
    const projectCode = findProject(form.project_id)?.code || ''
    const finalSiteCode = trimmedSiteCode || projectCode || ''
    
    // Construct batch payload
    const batchPayload = entries.value.map(entry => {
      let notes = form.notes.trim()
      let hours = entry.hours_worked
      let absences = 0
      
      if (!entry.isPresent) {
        hours = 0
        absences = 1
        const reason = entry.absenceReason
        notes = notes ? `Nieobecność: ${reason} | ${notes}` : `Nieobecność: ${reason}`
      }

      return {
        project_id: form.project_id!,
        date: new Date(form.date).toISOString(),
        site_code: finalSiteCode,
        team_member_id: entry.team_member_id,
        employee_count: 1, // Individual entry counts as 1
        hours_worked: hours,
        meals_served: entry.meals_served,
        overnight_stays: entry.overnight_stays,
        absences: absences,
        catering_company_id: form.catering_company_id,
        accommodation_company_id: form.accommodation_company_id,
        notes: notes || null
      }
    })

    await api<WorkLog[]>('/worklogs/batch', {
      method: 'POST',
      body: batchPayload
    })
    
    form.notes = ''
    await loadWorklogs()
    window.alert('Zapisano wpisy!')
  } catch (e) {
    console.error(e)
    window.alert('Wystąpił błąd podczas zapisywania.')
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
  dictionaryStore.hydrateFromStorage()
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

.member-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
}

.member-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.member-details {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-group-inline {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group-inline label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
}

.form-group-inline input {
  padding: 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
}

.absence-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background-color: #fef2f2; /* Light red for absence */
}

@media (prefers-color-scheme: dark) {
  .member-card {
    background: rgba(30, 41, 59, 0.5);
    border-color: rgba(148, 163, 184, 0.2);
  }
  
  .form-group-inline label {
    color: #94a3b8;
  }
  
  .form-group-inline input, .absence-select {
    background: rgba(15, 23, 42, 0.6);
    border-color: rgba(148, 163, 184, 0.3);
    color: white;
  }
  
  .absence-select {
    background-color: rgba(127, 29, 29, 0.3); /* Dark red for absence */
  }
}

.registration-form {
  max-width: 600px;
  /* margin-inline: auto; Removed for left alignment */
  width: 100%;
}
</style>
