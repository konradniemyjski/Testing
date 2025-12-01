<template>
  <div class="container">
    <MainNavigation :can-manage-users="canManageUsers" @logout="handleLogout" />
    <div class="card">
      <header class="page-header">
        <div>
          <h1>Słownik członków zespołu</h1>
          <p class="text-muted">Dodaj imiona i nazwiska osób współpracujących przy projektach.</p>
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
                placeholder="np. Anna Nowak"
              />
            </div>
            <p v-if="errorMessage" class="feedback feedback--error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="feedback feedback--success">{{ successMessage }}</p>
            <button class="primary-btn" type="submit">Dodaj osobę</button>
          </form>
        </div>

        <div>
          <h2>Zapisane osoby</h2>
          <table v-if="teamMembers.length" class="table">
            <thead>
              <tr>
                <th>Imię i nazwisko</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in teamMembers" :key="member.id">
                <td>{{ member.name }}</td>
                <td>
                  <button class="secondary-btn" type="button" @click="removeMember(member.id)">
                    Usuń
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">Brak osób na liście. Dodaj pierwszą po lewej.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useUserStore } from '~/stores/user'
import { useDictionaryStore } from '~/stores/dictionaries'

const userStore = useUserStore()
const dictionaryStore = useDictionaryStore()
const router = useRouter()
const canManageUsers = computed(() => userStore.profile?.role === 'admin')
const isAdmin = computed(() => userStore.profile?.role === 'admin')

const teamMembers = ref(dictionaryStore.teamMembers)
const form = reactive({
  name: ''
})
const errorMessage = ref('')
const successMessage = ref('')

function resetFeedback() {
  errorMessage.value = ''
  successMessage.value = ''
}

function addMember() {
  resetFeedback()
  const name = form.name.trim()

  if (!name) {
    errorMessage.value = 'Imię i nazwisko jest wymagane.'
    return
  }

  dictionaryStore.addTeamMember({ name })
  teamMembers.value = dictionaryStore.teamMembers

  form.name = ''
  successMessage.value = 'Dodano osobę do słownika zespołu.'
}

function removeMember(id: number) {
  dictionaryStore.removeTeamMember(id)
  teamMembers.value = dictionaryStore.teamMembers
}

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

onMounted(() => {
  userStore.hydrateFromStorage()
  dictionaryStore.hydrateFromStorage()
  teamMembers.value = dictionaryStore.teamMembers

  if (!userStore.isAuthenticated) {
    router.replace('/login')
    return
  }

  if (!isAdmin.value) {
    router.replace('/dashboard')
  }
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
