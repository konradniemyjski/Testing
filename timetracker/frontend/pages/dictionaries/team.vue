<template>
<<<<<<< ours
  <div class="container">
=======
  <div v-if="ready" class="container">
>>>>>>> theirs
    <MainNavigation :can-manage-users="canManageUsers" @logout="handleLogout" />
    <div class="card">
      <header class="page-header">
        <div>
<<<<<<< ours
          <h1>Słownik członków zespołu</h1>
          <p class="text-muted">Dodaj imiona i nazwiska osób współpracujących przy projektach.</p>
=======
          <h1>Administracja — członkowie zespołu</h1>
          <p class="text-muted">Dodaj osoby do słownika, aby wykorzystać je na panelu głównym.</p>
>>>>>>> theirs
        </div>
      </header>

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
<<<<<<< ours
                placeholder="np. Anna Nowak"
=======
                placeholder="np. Jan Kowalski"
>>>>>>> theirs
              />
            </div>
            <p v-if="errorMessage" class="feedback feedback--error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="feedback feedback--success">{{ successMessage }}</p>
<<<<<<< ours
            <button class="primary-btn" type="submit">Dodaj osobę</button>
=======
            <button class="primary-btn" type="submit" :disabled="submitting">
              {{ submitting ? 'Zapisywanie…' : 'Dodaj osobę' }}
            </button>
>>>>>>> theirs
          </form>
        </div>

        <div>
          <h2>Zapisane osoby</h2>
<<<<<<< ours
          <table v-if="teamMembers.length" class="table">
=======
          <table v-if="members.length" class="table">
>>>>>>> theirs
            <thead>
              <tr>
                <th>Imię i nazwisko</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
<<<<<<< ours
              <tr v-for="member in teamMembers" :key="member.id">
=======
              <tr v-for="member in members" :key="member.id">
>>>>>>> theirs
                <td>{{ member.name }}</td>
                <td>
                  <button class="secondary-btn" type="button" @click="removeMember(member.id)">
                    Usuń
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
<<<<<<< ours
          <p v-else class="text-muted">Brak osób na liście. Dodaj pierwszą po lewej.</p>
=======
          <p v-else class="text-muted">Brak osób w słowniku. Dodaj pierwszą po lewej.</p>
>>>>>>> theirs
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
<<<<<<< ours
import { useUserStore } from '~/stores/user'

type TeamMember = {
  id: number
  name: string
}

const userStore = useUserStore()
const router = useRouter()
const canManageUsers = computed(() => userStore.profile?.role === 'admin')

const teamMembers = ref<TeamMember[]>([])
=======
import { useDictionaryStore } from '~/stores/dictionaries'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

const userStore = useUserStore()
const dictionaryStore = useDictionaryStore()
const router = useRouter()
const canManageUsers = computed(() => userStore.profile?.role === 'admin')
const isAdmin = computed(() => userStore.profile?.role === 'admin')

const members = computed(() => dictionaryStore.teamMembers)
>>>>>>> theirs
const form = reactive({
  name: ''
})
const errorMessage = ref('')
const successMessage = ref('')
<<<<<<< ours
=======
const submitting = ref(false)
const ready = ref(false)
>>>>>>> theirs

function resetFeedback() {
  errorMessage.value = ''
  successMessage.value = ''
}

<<<<<<< ours
function addMember() {
=======
async function addMember() {
>>>>>>> theirs
  resetFeedback()
  const name = form.name.trim()

  if (!name) {
<<<<<<< ours
    errorMessage.value = 'Imię i nazwisko jest wymagane.'
    return
  }

  teamMembers.value.push({
    id: Date.now(),
    name
  })

  form.name = ''
  successMessage.value = 'Dodano osobę do słownika zespołu.'
}

function removeMember(id: number) {
  teamMembers.value = teamMembers.value.filter((member) => member.id !== id)
=======
    errorMessage.value = 'Podaj imię i nazwisko osoby.'
    return
  }

  try {
    submitting.value = true
    await dictionaryStore.createTeamMember({ name })
    form.name = ''
    successMessage.value = 'Dodano osobę do słownika zespołu.'
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'Nie udało się zapisać osoby.'
  } finally {
    submitting.value = false
  }
}

async function removeMember(id: number) {
  await dictionaryStore.deleteTeamMember(id)
>>>>>>> theirs
}

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

<<<<<<< ours
onMounted(() => {
  userStore.hydrateFromStorage()
  if (!userStore.isAuthenticated) {
    router.replace('/login')
  }
=======
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

  await dictionaryStore.fetchDictionaries()
  ready.value = true
>>>>>>> theirs
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
</style>
