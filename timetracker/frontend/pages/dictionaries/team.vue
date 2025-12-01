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
            <p v-if="errorMessage" class="feedback feedback--error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="feedback feedback--success">{{ successMessage }}</p>
            <button class="primary-btn" type="submit" :disabled="submitting">
              {{ submitting ? 'Zapisywanie…' : 'Dodaj osobę' }}
            </button>
          </form>
        </div>

        <div>
          <h2>Zapisane osoby</h2>
          <table v-if="members.length" class="table">
            <thead>
              <tr>
                <th>Imię i nazwisko</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in members" :key="member.id">
                <td>{{ member.name }}</td>
                <td>
                  <button class="secondary-btn" type="button" @click="removeMember(member.id)">
                    Usuń
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">Brak osób w słowniku. Dodaj pierwszą po lewej.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useDictionaryStore } from '~/stores/dictionaries'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

const userStore = useUserStore()
const dictionaryStore = useDictionaryStore()
const router = useRouter()
const canManageUsers = computed(() => userStore.profile?.role === 'admin')
const isAdmin = computed(() => userStore.profile?.role === 'admin')

const members = computed(() => dictionaryStore.teamMembers)
const form = reactive({
  name: ''
})
const errorMessage = ref('')
const successMessage = ref('')
const submitting = ref(false)
const ready = ref(false)

function resetFeedback() {
  errorMessage.value = ''
  successMessage.value = ''
}

async function addMember() {
  resetFeedback()
  const name = form.name.trim()

  if (!name) {
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

  await dictionaryStore.fetchDictionaries()
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
