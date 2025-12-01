<template>
  <div v-if="ready" class="container">
    <MainNavigation :can-manage-users="canManageUsers" @logout="handleLogout" />
    <div class="card">
      <header class="page-header">
        <div>
          <h1>Administracja — członkowie zespołu</h1>
          <p class="text-muted">Dodaj osoby do słownika, aby wykorzystać je na panelu głównym.</p>
        </div>
      </header>

      <section class="card-section">
        <div class="form-group">
          <label for="teamSelector">Zespół</label>
          <select id="teamSelector" v-model.number="selectedTeamId">
            <option v-for="team in teams" :key="team.id" :value="team.id">
              {{ team.name }}
            </option>
          </select>
        </div>
        <p class="text-muted selector-hint">
          Wybierz zespół, aby zarządzać przypisanymi do niego osobami.
        </p>
      </section>

      <section class="grid-section">
        <div>
          <h2>Dodaj osobę</h2>
          <form class="entry-form" @submit.prevent="addMember">
            <div class="form-group">
              <label for="teamMemberName">Imię i nazwisko</label>
              <input
                id="teamMemberName"
                v-model="form.name"
                type="text"
                required
                placeholder="np. Jan Kowalski"
              />
            </div>
            <div class="form-group">
              <label for="teamMemberTeam">Zespół</label>
              <select id="teamMemberTeam" v-model.number="form.team_id" required>
                <option v-for="team in teams" :key="team.id" :value="team.id">
                  {{ team.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="teamMemberRole">Rola</label>
              <select id="teamMemberRole" v-model="form.role">
                <option v-for="role in roleOptions" :key="role" :value="role">{{ role }}</option>
              </select>
            </div>
            <p v-if="memberFormError" class="feedback feedback--error">{{ memberFormError }}</p>
            <p v-if="memberFormSuccess" class="feedback feedback--success">{{ memberFormSuccess }}</p>
            <button class="primary-btn" type="submit" :disabled="submitting">
              {{ submitting ? 'Zapisywanie…' : 'Dodaj osobę' }}
            </button>
          </form>
        </div>

        <div>
          <h2>Zapisane osoby</h2>
          <p v-if="membersError" class="feedback feedback--error">{{ membersError }}</p>
          <p v-if="membersSuccess" class="feedback feedback--success">{{ membersSuccess }}</p>
          <table v-if="members.length" class="table">
            <thead>
              <tr>
                <th>Imię i nazwisko</th>
                <th>Zespół</th>
                <th>Rola</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in members" :key="member.id">
                <td>
                  <input
                    v-model="editableMembers[member.id].name"
                    type="text"
                    required
                    placeholder="Imię i nazwisko"
                  />
                </td>
                <td>
                  <select v-model.number="editableMembers[member.id].team_id">
                    <option v-for="team in teams" :key="team.id" :value="team.id">
                      {{ team.name }}
                    </option>
                  </select>
                </td>
                <td>
                  <select v-model="editableMembers[member.id].role">
                    <option v-for="role in roleOptions" :key="role" :value="role">{{ role }}</option>
                  </select>
                </td>
                <td class="member-actions">
                  <button
                    class="secondary-btn"
                    type="button"
                    :disabled="isMemberSaving(member.id)"
                    @click="saveMember(member.id)"
                  >
                    {{ isMemberSaving(member.id) ? 'Zapisywanie…' : 'Zapisz' }}
                  </button>
                  <button
                    class="secondary-btn"
                    type="button"
                    :disabled="isMemberSaving(member.id)"
                    @click="removeMember(member.id)"
                  >
                    Usuń
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">Brak osób w słowniku. Dodaj pierwszą po lewej.</p>
        </div>
      </section>

      <section class="card-section card-section--teams">
        <h2>Nazwa zespołu</h2>
        <form class="entry-form" @submit.prevent="saveTeamName">
          <div class="form-group">
            <label for="teamNameInput">Edytuj nazwę wybranego zespołu</label>
            <input
              id="teamNameInput"
              v-model="teamName"
              type="text"
              required
              placeholder="np. Brygada A"
            />
          </div>
          <p v-if="teamError" class="feedback feedback--error">{{ teamError }}</p>
          <p v-if="teamSuccess" class="feedback feedback--success">{{ teamSuccess }}</p>
          <button class="primary-btn" type="submit" :disabled="teamSubmitting">
            {{ teamSubmitting ? 'Zapisywanie…' : 'Zapisz nazwę' }}
          </button>
        </form>

        <hr class="section-divider" />

        <h3>Dodaj nowy zespół</h3>
        <form class="entry-form" @submit.prevent="createTeam">
          <div class="form-group">
            <label for="newTeamName">Nazwa zespołu</label>
            <input
              id="newTeamName"
              v-model="newTeamName"
              type="text"
              required
              placeholder="np. Brygada B"
            />
          </div>
          <p v-if="newTeamError" class="feedback feedback--error">{{ newTeamError }}</p>
          <p v-if="newTeamSuccess" class="feedback feedback--success">{{ newTeamSuccess }}</p>
          <button class="secondary-btn" type="submit" :disabled="newTeamSubmitting">
            {{ newTeamSubmitting ? 'Dodawanie…' : 'Dodaj zespół' }}
          </button>
        </form>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useDictionaryStore, type TeamMemberRole } from '~/stores/dictionaries'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

const userStore = useUserStore()
const dictionaryStore = useDictionaryStore()
const router = useRouter()
const canManageUsers = computed(() => userStore.profile?.role === 'admin')
const isAdmin = computed(() => userStore.profile?.role === 'admin')

const teams = computed(() => dictionaryStore.teams)
const selectedTeamId = ref<number | null>(null)
const selectedTeam = computed(() =>
  teams.value.find((team) => team.id === selectedTeamId.value) || null
)
const members = computed(() => selectedTeam.value?.members ?? [])

const teamName = ref('')
const teamError = ref('')
const teamSuccess = ref('')
const teamSubmitting = ref(false)

const newTeamName = ref('')
const newTeamError = ref('')
const newTeamSuccess = ref('')
const newTeamSubmitting = ref(false)

const form = reactive({
  name: '',
  role: 'Pracownik' as TeamMemberRole,
  team_id: null as number | null
})
const memberFormError = ref('')
const memberFormSuccess = ref('')
const submitting = ref(false)

const membersError = ref('')
const membersSuccess = ref('')
const ready = ref(false)

const editableMembers = reactive<
  Record<number, { name: string; role: TeamMemberRole; team_id: number | null }>
>({})
const savingMembers = reactive<Record<number, boolean>>({})
const roleOptions: TeamMemberRole[] = ['Pracownik', 'Brygadzista']

function resetFeedback() {
  teamError.value = ''
  teamSuccess.value = ''
  newTeamError.value = ''
  newTeamSuccess.value = ''
  memberFormError.value = ''
  memberFormSuccess.value = ''
  membersError.value = ''
  membersSuccess.value = ''
}

watch(
  teams,
  (list) => {
    if (!list.length) return
    if (selectedTeamId.value == null || !list.some((team) => team.id === selectedTeamId.value)) {
      selectedTeamId.value = list[0].id
    }
  },
  { immediate: true }
)

watch(
  selectedTeam,
  (team) => {
    teamName.value = team?.name || ''
    form.team_id = team?.id ?? null
  },
  { immediate: true }
)

watch(
  members,
  (list) => {
    const ids = new Set(list.map((member) => member.id))

    Object.keys(editableMembers).forEach((id) => {
      if (!ids.has(Number(id))) {
        delete editableMembers[Number(id)]
      }
    })

    list.forEach((member) => {
      editableMembers[member.id] = {
        name: member.name,
        role: member.role,
        team_id: member.team_id
      }
    })
  },
  { immediate: true }
)

async function saveTeamName() {
  resetFeedback()
  const name = teamName.value.trim()
  if (!selectedTeam.value) {
    teamError.value = 'Wybierz zespół do edycji.'
    return
  }

  if (!name) {
    teamError.value = 'Podaj nazwę zespołu.'
    return
  }

  try {
    teamSubmitting.value = true
    const updatedTeam = await dictionaryStore.updateTeam(selectedTeam.value.id, name)
    teamName.value = updatedTeam.name
    teamSuccess.value = 'Zapisano nazwę zespołu.'
  } catch (error: any) {
    teamError.value = error?.data?.detail || 'Nie udało się zapisać nazwy zespołu.'
  } finally {
    teamSubmitting.value = false
  }
}

async function createTeam() {
  resetFeedback()
  const name = newTeamName.value.trim()

  if (!name) {
    newTeamError.value = 'Podaj nazwę zespołu.'
    return
  }

  try {
    newTeamSubmitting.value = true
    const created = await dictionaryStore.createTeam(name)
    selectedTeamId.value = created.id
    teamSuccess.value = ''
    newTeamSuccess.value = 'Dodano nowy zespół.'
    newTeamName.value = ''
  } catch (error: any) {
    newTeamError.value = error?.data?.detail || 'Nie udało się utworzyć zespołu.'
  } finally {
    newTeamSubmitting.value = false
  }
}

async function addMember() {
  resetFeedback()
  const name = form.name.trim()
  const teamId = form.team_id || selectedTeamId.value

  if (!name) {
    memberFormError.value = 'Podaj imię i nazwisko osoby.'
    return
  }

  if (!teamId) {
    memberFormError.value = 'Wybierz zespół dla tej osoby.'
    return
  }

  try {
    submitting.value = true
    await dictionaryStore.createTeamMember({
      name,
      role: form.role,
      team_id: teamId
    })
    form.name = ''
    form.role = 'Pracownik'
    form.team_id = selectedTeamId.value
    memberFormSuccess.value = 'Dodano osobę do słownika zespołu.'
  } catch (error: any) {
    memberFormError.value = error?.data?.detail || 'Nie udało się zapisać osoby.'
  } finally {
    submitting.value = false
  }
}

function setMemberSaving(id: number, value: boolean) {
  savingMembers[id] = value
}

function isMemberSaving(id: number) {
  return savingMembers[id] || false
}

async function saveMember(memberId: number) {
  resetFeedback()
  const memberDraft = editableMembers[memberId]

  if (!memberDraft || !memberDraft.name.trim()) {
    membersError.value = 'Imię i nazwisko nie mogą być puste.'
    return
  }

  const teamId = memberDraft.team_id || selectedTeamId.value
  if (!teamId) {
    membersError.value = 'Wybierz zespół dla tej osoby.'
    return
  }

  try {
    setMemberSaving(memberId, true)
    await dictionaryStore.updateTeamMember(memberId, {
      name: memberDraft.name.trim(),
      role: memberDraft.role,
      team_id: teamId
    })
    membersSuccess.value = 'Zapisano zmiany dla członka zespołu.'
  } catch (error: any) {
    membersError.value = error?.data?.detail || 'Nie udało się zaktualizować osoby.'
  } finally {
    setMemberSaving(memberId, false)
  }
}

async function removeMember(id: number) {
  resetFeedback()
  try {
    setMemberSaving(id, true)
    await dictionaryStore.deleteTeamMember(id)
    membersSuccess.value = 'Usunięto osobę z zespołu.'
  } catch (error: any) {
    membersError.value = error?.data?.detail || 'Nie udało się usunąć osoby.'
  } finally {
    setMemberSaving(id, false)
  }
}

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

onMounted(async () => {
  userStore.hydrateFromStorage()
  if (!userStore.isAuthenticated) {
    router.replace('/login')
    return
  }

  if (!isAdmin.value) {
    router.replace('/dashboard')
    return
  }

  await dictionaryStore.fetchDictionaries(true)
  if (teams.value.length && selectedTeamId.value == null) {
    selectedTeamId.value = teams.value[0].id
  }
  form.team_id = selectedTeamId.value
  ready.value = true
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.grid-section {
  margin-top: 2rem;
  display: grid;
  gap: 1.75rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.card-section {
  margin-top: 1.5rem;
}

.card-section--teams {
  margin-top: 2.5rem;
}

.selector-hint {
  margin: 0.35rem 0 0;
}

.section-divider {
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin: 1.5rem 0;
}

.entry-form {
  display: grid;
  gap: 1rem;
}

.feedback {
  margin: 0;
  font-weight: 600;
}

.feedback--error {
  color: #ef4444;
}

.feedback--success {
  color: #16a34a;
}

.member-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
</style>
