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
              <input 
                id="siteCode" 
                v-model="form.site_code" 
                type="text" 
                readonly 
                class="readonly-input"
                tabindex="-1"
              />
            </div>

            <div class="form-group" v-if="!isUser">
              <label for="teamSelect">Zespół</label>
              <select
                id="teamSelect"
                v-model.number="selectedTeamId"
                :disabled="!teams.length"
              >
                <option :value="null">Wybierz zespół</option>
                <option v-for="team in teams" :key="team.id" :value="team.id">
                  {{ team.name || 'Bez nazwy' }}
                </option>
              </select>
            </div>

            <!-- Bulk Entry Section -->
            <div v-if="(selectedTeamId || entries.length) || isUser" class="bulk-entry-section">
              <h3 v-if="!isUser">Pracownicy</h3>
              <h3 v-else>Twoje godziny</h3>
              
              <div 
                v-for="(entry, index) in entries" 
                :key="index" 
                class="member-card"
                :class="{ 'absent': !entry.isPresent }"
              >
                <div class="member-header">
                  <div class="member-identity">
                    <!-- If manual entry, show select. If pre-filled team member, show text -->
                    <strong v-if="!entry.isManual">
                      {{ findTeamMember(entry.team_member_id)?.name || (isUser ? 'Mój własny wpis' : 'Nieznany') }}
                    </strong>
                    <select 
                      v-else 
                      v-model.number="entry.team_member_id" 
                      class="member-select"
                      required
                    >
                      <option :value="null" disabled>Wybierz pracownika</option>
                      <option v-for="m in getAvailableMembers(entry)" :key="m.id" :value="m.id">
                        {{ m.name }}
                      </option>
                    </select>
                  </div>

                  <div class="attendance-toggle">
                    <label>
                      <input type="checkbox" v-model="entry.isPresent"> 
                      {{ entry.isPresent ? 'Obecny' : 'Nieobecny' }}
                    </label>
                    <button 
                      v-if="entry.isManual && !isUser" 
                      type="button" 
                      @click="removeEntry(index)"
                      class="delete-entry-btn"
                      title="Usuń"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                <div class="member-body">
                  <div v-if="entry.isPresent" class="member-details">
                    <div class="form-group-inline">
                      <label>Godziny</label>
                      <input type="number" v-model.number="entry.hours_worked" min="0.25" step="0.25" style="width: 80px">
                    </div>
                    <div class="form-group-inline">
                      <label>Posiłki</label>
                      <input type="number" v-model.number="entry.meals_served" min="0" style="width: 60px">
                    </div>
                    <div class="form-group-inline">
                      <label>Nocleg</label>
                      <select v-model.number="entry.overnight_stays" style="width: 70px">
                        <option :value="0">Nie</option>
                        <option :value="1">Tak</option>
                      </select>
                    </div>
                  </div>

                  <div v-else class="member-absence">
                     <div class="form-group-inline">
                        <label>Powód nieobecności</label>
                        <select v-model="entry.absenceReason" class="absence-select">
                          <option value="Urlop">Urlop</option>
                          <option value="L4">L4</option>
                          <option value="Inne">Inne</option>
                          <option value="Nieusprawiedliwiona">Nieusprawiedliwiona</option>
                        </select>
                     </div>
                     <div class="form-group-inline" style="flex-grow: 1;">
                        <label>Komentarz</label>
                        <input 
                          type="text" 
                          v-model="entry.absenceComment" 
                          placeholder="Np. wizyta lekarska"
                          class="absence-comment-input"
                        >
                     </div>
                     <!-- Disabled fields implementation visual only, kept hidden or shown disabled if requested. 
                          User said: "Obecny: Nie -> Jacek Bonacek (Szary niemożliwy do kliknięcia)". 
                          So I basically hide editable fields and show absence reason. -->
                     <div class="member-details disabled-view">
                        <div class="form-group-inline disabled">
                          <label>Godziny</label>
                          <input type="text" value="0" disabled style="width: 80px">
                        </div>
                        <div class="form-group-inline disabled">
                          <label>Posiłki</label>
                          <input type="text" value="0" disabled style="width: 60px">
                        </div>
                     </div>
                  </div>
                </div>
              </div>

              <div class="add-member-container" v-if="!isUser">
                <button 
                  type="button" 
                  class="secondary-btn" 
                  @click="addManualMember"
                  :disabled="!canAddMember"
                >
                  + Dodaj pracownika
                </button>
              </div>
            </div>

            <!-- Common Fields for Bulk -->
            <div class="form-group" style="margin-top: 2rem; border-top: 1px solid #e2e8f0; padding-top: 1rem;">
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
              <label for="notes">Uwagi do całego wpisu</label>
              <textarea
                id="notes"
                v-model="form.notes"
                rows="3"
                placeholder="Dodatkowe informacje..."
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
            <div style="display: flex; gap: 0.5rem; align-items: center;">
              <select v-model="pageSize" @change="handlePageSizeChange" style="padding: 0.25rem; border-radius: 4px; border: 1px solid #ccc;">
                <option :value="10">10 na stronę</option>
                <option :value="25">25 na stronę</option>
                <option :value="50">50 na stronę</option>
              </select>
              <button
                class="primary-btn"
                type="button"
                @click="exportWorklogs"
                :disabled="exporting || !worklogs.length"
              >
                {{ exporting ? 'Przygotowywanie…' : 'Eksportuj do XLSX' }}
              </button>
            </div>
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

          
          <!-- Pagination Controls -->
          <div v-if="totalPages > 1" class="pagination-controls">
            <button @click="changePage(1)" :disabled="currentPage === 1" class="pagination-btn">
              &lt;&lt;
            </button>
            <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="pagination-btn">
              &lt;
            </button>
            
            <span class="pagination-info">
              Strona {{ currentPage }} z {{ totalPages }}
            </span>
            
            <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="pagination-btn">
              &gt;
            </button>
            <button @click="changePage(totalPages)" :disabled="currentPage === totalPages" class="pagination-btn">
              &gt;&gt;
            </button>
          </div>
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

type PaginatedWorkLogs = {
  items: WorkLog[]
  total: number
  page: number
  size: number
  pages: number
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
// Pagination state
const currentPage = ref(1)
const pageSize = ref(25)
const totalItems = ref(0)
const totalPages = ref(0)

const saving = ref(false)
const exporting = ref(false)
const ready = ref(false)

type BatchEntry = {
  team_member_id: number | null
  isPresent: boolean
  hours_worked: number
  meals_served: number
  overnight_stays: number
  absenceReason: string
  absenceComment?: string
  isManual: boolean
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

const isUser = computed(() => userStore.profile?.role === 'user')

const { teams, teamMembers, accommodationCompanies, cateringCompanies } = storeToRefs(dictionaryStore)

const selectedTeamId = ref<number | null>(null)
const filteredTeamMembers = computed(() => {
  if (selectedTeamId.value == null) {
    return teamMembers.value
  }
  return teamMembers.value.filter((member) => member.team_id === selectedTeamId.value)
  return teamMembers.value.filter((member) => member.team_id === selectedTeamId.value)
})

const canAddMember = computed(() => {
  // Count unique selected IDs (excluding nulls)
  const selectedIds = new Set(
    entries.value
      .map(e => e.team_member_id)
      .filter((id): id is number => id != null)
  )
  // If we have selected everyone from the dictionary, we can't add more
  return selectedIds.size < teamMembers.value.length
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
  const fetchedProjects = await api<Project[]>('/projects/')
  projects.value = fetchedProjects.sort((a, b) => a.code.localeCompare(b.code))
  if (!form.project_id && projects.value.length) {
    form.project_id = projects.value[0].id
    form.site_code = projects.value[0].code
  }
}

async function loadWorklogs() {
  try {
    const response = await api<PaginatedWorkLogs>('/worklogs/', {
      params: {
        page: currentPage.value,
        size: pageSize.value
      }
    })
    worklogs.value = response.items
    totalItems.value = response.total
    totalPages.value = response.pages
  } catch (e) {
    console.error('Failed to load worklogs', e)
  }
}

async function changePage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  await loadWorklogs()
}

async function handlePageSizeChange() {
  currentPage.value = 1
  await loadWorklogs()
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
    if (teamList.length && selectedTeamId.value == null && !isUser.value) {
      selectedTeamId.value = teamList[0].id
    }
  },
  { immediate: true }
)

watch(selectedTeamId, async (newId) => {
  if (isUser.value) return

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
    absenceReason: 'Urlop',
    absenceComment: '',
    isManual: false
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

watch(isUser, (val) => {
  if (val) {
    // If user, initialize one empty entry for themselves
    entries.value = [{
      team_member_id: null,
      isPresent: true,
      hours_worked: 8,
      meals_served: 0,
      overnight_stays: 0,
      absenceReason: 'Urlop',
      absenceComment: '',
      isManual: false
    }]
    // Clear selected team to prevent interference
    selectedTeamId.value = null
  }
}, { immediate: true })


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

function getAvailableMembers(currentEntry: BatchEntry) {
  const selectedIds = new Set(
    entries.value
      .map(e => e.team_member_id)
      .filter((id): id is number => id != null)
  )
  return teamMembers.value.filter(m => 
    !selectedIds.has(m.id) || m.id === currentEntry.team_member_id
  )
}

async function addManualMember() {
  entries.value.push({
    team_member_id: null,
    isPresent: true,
    hours_worked: 8,
    meals_served: 0,
    overnight_stays: 0,
    absenceReason: 'Urlop'
  })
}

async function handleCreate() {
  if (!form.project_id) return
  
  try {
    saving.value = true
    const trimmedSiteCode = form.site_code.trim()
    const projectCode = findProject(form.project_id)?.code || ''
    const finalSiteCode = trimmedSiteCode || projectCode || ''
    
    // Construct batch payload
    const batchPayload = entries.value
      .filter(e => isUser.value || e.team_member_id != null) // Allow null team_member_id if isUser
      .map(entry => {
        let notes = form.notes.trim()
        let hours = entry.hours_worked
        let absences = 0
        
        if (!entry.isPresent) {
          hours = 0
          absences = 1
          const reason = entry.absenceReason
          const comment = entry.absenceComment ? ` (${entry.absenceComment})` : ''
          notes = notes ? `Nieobecność: ${reason}${comment} | ${notes}` : `Nieobecność: ${reason}${comment}`
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
    
    if (batchPayload.length === 0) {
      window.alert('Brak pracowników do zapisania.')
      return
    }

    await api<WorkLog[]>('/worklogs/batch', {
      method: 'POST',
      body: batchPayload
    })
    
    form.notes = ''
    await loadWorklogs()
    
    // Reset form for next entry
    if (isUser.value) {
      entries.value = [{
        team_member_id: null,
        isPresent: true,
        hours_worked: 8,
        meals_served: 0,
        overnight_stays: 0,
        absenceReason: 'Urlop',
        absenceComment: '',
        isManual: false
      }]
    } else if (selectedTeamId.value) {
      // Refresh logic for admin/team view if needed, but for now leave as is or basic reset
       entries.value.forEach(e => {
         e.hours_worked = 8
         e.meals_served = 0
         e.overnight_stays = 0
         e.isPresent = true
         e.notes = '' // Custom field not in BatchEntry type but pushed to payload
       })
    }

    window.alert('Zapisano wpisy! Lista została odświeżona.')
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
  transition: all 0.2s;
}

.member-card.absent {
  background: #f1f5f9;
  border-color: #cbd5e1;
  opacity: 0.9;
}

.member-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.member-body {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.member-details {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.member-details.disabled-view {
  opacity: 0.5;
  pointer-events: none;
}

.member-absence {
  display: flex;
  gap: 1rem;
  width: 100%;
}

.attendance-toggle label {
  cursor: pointer;
  font-weight: 500;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.pagination-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f3f3f3;
}

.pagination-info {
  font-weight: 500;
  margin: 0 0.5rem;
}

.add-member-container {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
  margin-bottom: 2rem;
}

.secondary-btn {
  background: transparent;
  border: 1px dashed #64748b;
  color: #64748b;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.secondary-btn:hover {
  background: #f1f5f9;
  border-color: #475569;
  color: #475569;
}

.secondary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-style: solid;
}


@media (prefers-color-scheme: dark) {
  .member-card {
    background: rgba(30, 41, 59, 0.5);
    border-color: rgba(148, 163, 184, 0.2);
  }
  
  .form-group-inline label {
    color: #94a3b8;
  }
  
  .absence-select, .absence-comment-input {
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

.readonly-input {
  background-color: #f1f5f9;
  color: #64748b;
  cursor: not-allowed;
  background-color: #fff;
}

.absence-comment-input {
  padding: 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  width: 100%;
}

@media (prefers-color-scheme: dark) {
  .readonly-input {
    background-color: rgba(15, 23, 42, 0.6);
    color: #94a3b8;
    border-color: rgba(148, 163, 184, 0.2);
  }

  /* Fix for absent card in dark mode */
  .member-card.absent {
    background: rgba(127, 29, 29, 0.15); /* Subtle dark red/faded background */
    border-color: rgba(220, 38, 38, 0.2);
  }
}

.delete-entry-btn {
  background: none;
  border: none;
  color: #ef4444;
  font-weight: bold;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  margin-left: 0.5rem;
  border-radius: 4px;
}
.delete-entry-btn:hover {
  background-color: #fee2e2;
}
</style>
