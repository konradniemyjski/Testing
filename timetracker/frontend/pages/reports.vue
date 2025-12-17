<template>
  <div v-if="ready" class="container">
    <MainNavigation :can-manage-users="true" @logout="handleLogout" />
    
    <div class="card">
      <header>
        <h1>Zaawansowane Raporty</h1>
        <p class="text-muted">Generuj szczegółowe zestawienia danych.</p>
      </header>
      
      <div class="reports-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          class="tab-btn" 
          :class="{ active: currentTab === tab.id }"
          @click="currentTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="report-content">
        <!-- 1. Uczestnicy wg Budowy -->
        <div v-if="currentTab === 'participants'">
          <div class="filters">
            <div class="form-group">
              <label>Budowa</label>
              <select v-model="filters.projectId">
                <option :value="null" disabled>Wybierz budowę</option>
                <option v-for="p in projects" :key="p.id" :value="p.id">
                  {{ p.name }} ({{ p.code }})
                </option>
              </select>
            </div>
            <button class="primary-btn" @click="loadParticipants" :disabled="!filters.projectId || loading">
              Generuj
            </button>
          </div>
          
          <div v-if="participants.length" class="results">
            <h3>Lista uczestników ({{ participants.length }})</h3>
            <ul class="participant-list">
              <li v-for="name in participants" :key="name">{{ name }}</li>
            </ul>
          </div>
          <p v-else-if="searched && !participants.length" class="text-muted">Brak danych dla wybranej budowy.</p>
        </div>

        <!-- 2. Praca Zespołu -->
        <div v-if="currentTab === 'teamwork'">
          <div class="filters">
            <div class="form-group">
              <label>Zespół</label>
              <select v-model="filters.teamId">
                <option :value="null" disabled>Wybierz zespół</option>
                <option v-for="t in teams" :key="t.id" :value="t.id">
                  {{ t.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Od</label>
              <input type="date" v-model="filters.startDate">
            </div>
            <div class="form-group">
              <label>Do</label>
              <input type="date" v-model="filters.endDate">
            </div>
            <button class="primary-btn" @click="loadTeamWork" :disabled="!filters.teamId || loading">
              Szukaj
            </button>
          </div>
          
          <ReportTable 
            v-if="worklogs.length" 
            :data="worklogs" 
            :total="totalItems" 
            :page="currentPage" 
            :pages="totalPages"
            @page-change="changePage"
          />
          <p v-else-if="searched && !worklogs.length" class="text-muted">Brak wpisów.</p>
        </div>

        <!-- 3. Noclegi -->
        <div v-if="currentTab === 'accommodation'">
          <div class="filters">
            <div class="form-group">
              <label>Firma (opcjonalnie)</label>
              <select v-model="filters.companyId">
                <option :value="null">Wszystkie</option>
                <option v-for="c in accommodationCompanies" :key="c.id" :value="c.id">
                  {{ c.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Od</label>
              <input type="date" v-model="filters.startDate">
            </div>
            <div class="form-group">
              <label>Do</label>
              <input type="date" v-model="filters.endDate">
            </div>
            <button class="primary-btn" @click="loadAccommodation" :disabled="loading">
              Szukaj
            </button>
          </div>
          
          <ReportTable 
            v-if="worklogs.length" 
            :data="worklogs" 
            :total="totalItems"
            :page="currentPage"
            :pages="totalPages"
            type="accommodation"
            @page-change="changePage"
          />
           <p v-else-if="searched && !worklogs.length" class="text-muted">Brak wpisów.</p>
        </div>

        <!-- 4. Posiłki -->
        <div v-if="currentTab === 'catering'">
          <div class="filters">
            <div class="form-group">
              <label>Firma (opcjonalnie)</label>
              <select v-model="filters.companyId">
                <option :value="null">Wszystkie</option>
                <option v-for="c in cateringCompanies" :key="c.id" :value="c.id">
                  {{ c.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Od</label>
              <input type="date" v-model="filters.startDate">
            </div>
            <div class="form-group">
              <label>Do</label>
              <input type="date" v-model="filters.endDate">
            </div>
            <button class="primary-btn" @click="loadCatering" :disabled="loading">
              Szukaj
            </button>
          </div>
          
          <ReportTable 
            v-if="worklogs.length" 
            :data="worklogs" 
            :total="totalItems"
            :page="currentPage"
            :pages="totalPages"
            type="catering"
            @page-change="changePage"
          />
           <p v-else-if="searched && !worklogs.length" class="text-muted">Brak wpisów.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useDictionaryStore } from '~/stores/dictionaries'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

const tabs = [
  { id: 'participants', label: 'Uczestnicy wg Budowy' },
  { id: 'teamwork', label: 'Praca Zespołu' },
  { id: 'accommodation', label: 'Noclegi' },
  { id: 'catering', label: 'Posiłki' }
]

const currentTab = ref('participants')
const ready = ref(false)
const loading = ref(false)
const searched = ref(false)

const projects = ref<any[]>([])
const participants = ref<string[]>([])
const worklogs = ref<any[]>([])
const totalItems = ref(0)
const currentPage = ref(1)
const totalPages = ref(0)
const pageSize = 50

const filters = reactive({
  projectId: null as number | null,
  teamId: null as number | null,
  companyId: null as number | null,
  startDate: new Date(new Date().setDate(1)).toISOString().slice(0, 10), // First day of current month
  endDate: new Date().toISOString().slice(0, 10)
})

const userStore = useUserStore()
const dictionaryStore = useDictionaryStore()
const api = useApi()
const router = useRouter()

const { teams, accommodationCompanies, cateringCompanies } = storeToRefs(dictionaryStore)

// Fetch projects manually as they are not in dictionary store? Or maybe they are?
// In dashboard calling /projects/ so let's use that.
async function loadProjects() {
  projects.value = await api('/projects/')
}

async function loadParticipants() {
  if (!filters.projectId) return
  loading.value = true
  searched.value = false
  try {
    participants.value = await api('/reports/participants', {
      params: { project_id: filters.projectId }
    })
    searched.value = true
  } finally {
    loading.value = false
  }
}

async function loadTeamWork() {
  if (!filters.teamId) return
  loading.value = true
  searched.value = false
  try {
    const res: any = await api('/reports/team-work', {
      params: {
        team_id: filters.teamId,
        start_date: filters.startDate,
        end_date: filters.endDate,
        page: currentPage.value,
        size: pageSize
      }
    })
    worklogs.value = res.items
    totalItems.value = res.total
    totalPages.value = res.pages
    searched.value = true
  } finally {
    loading.value = false
  }
}

async function loadAccommodation() {
  loading.value = true
  searched.value = false
  try {
    const params: any = {
      start_date: filters.startDate,
      end_date: filters.endDate,
      page: currentPage.value,
      size: pageSize
    }
    if (filters.companyId) params.company_id = filters.companyId
    
    const res: any = await api('/reports/accommodation', { params })
    worklogs.value = res.items
    totalItems.value = res.total
    totalPages.value = res.pages
    searched.value = true
  } finally {
    loading.value = false
  }
}

async function loadCatering() {
  loading.value = true
  searched.value = false
  try {
    const params: any = {
      start_date: filters.startDate,
      end_date: filters.endDate,
      page: currentPage.value,
      size: pageSize
    }
    if (filters.companyId) params.company_id = filters.companyId
    
    const res: any = await api('/reports/catering', { params })
    worklogs.value = res.items
    totalItems.value = res.total
    totalPages.value = res.pages
    searched.value = true
  } finally {
    loading.value = false
  }
}

function changePage(p: number) {
  currentPage.value = p
  if (currentTab.value === 'teamwork') loadTeamWork()
  else if (currentTab.value === 'accommodation') loadAccommodation()
  else if (currentTab.value === 'catering') loadCatering()
}

// Reset state when tab changes
watch(currentTab, () => {
  participants.value = []
  worklogs.value = []
  searched.value = false
  currentPage.value = 1
  totalItems.value = 0
  // Reset filters if needed, but keeping dates is usually friendly
  filters.projectId = null
  filters.teamId = null
  filters.companyId = null
})

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

onMounted(async () => {
  userStore.hydrateFromStorage()
  dictionaryStore.hydrateFromStorage()
  if (!userStore.isAuthenticated || userStore.profile?.role !== 'admin') {
    router.replace('/dashboard')
    return
  }
  
  await Promise.all([
    dictionaryStore.fetchDictionaries(),
    loadProjects()
  ])
  ready.value = true
})
</script>

<style scoped>
.reports-tabs {
  display: flex;
  gap: 1rem;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 2rem;
  overflow-x: auto;
}

.tab-btn {
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #000;
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.filters {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 0;
}

.participant-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
  list-style: none;
  padding: 0;
}

.participant-list li {
  padding: 0.5rem;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
}
</style>
