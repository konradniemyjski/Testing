<template>
  <div class="container">
    <MainNavigation :can-manage-users="canManageUsers" @logout="handleLogout" />
    <div class="card">
      <header class="page-header">
        <div>
          <h1>Słownik firm cateringowych</h1>
          <p class="text-muted">Dodaj NIP oraz nazwę firm obsługujących posiłki.</p>
        </div>
      </header>

      <section class="grid-section">
        <div>
          <h2>Dodaj firmę</h2>
          <form class="entry-form" @submit.prevent="addCompany">
            <div class="form-group">
              <label for="cateringTaxId">NIP</label>
              <input
                id="cateringTaxId"
                v-model="form.taxId"
                type="text"
                required
                placeholder="np. 123-456-78-90"
              />
            </div>
            <div class="form-group">
              <label for="cateringName">Nazwa firmy</label>
              <input
                id="cateringName"
                v-model="form.name"
                type="text"
                required
                placeholder="np. Smaczny Catering Sp. z o.o."
              />
            </div>
            <p v-if="errorMessage" class="feedback feedback--error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="feedback feedback--success">{{ successMessage }}</p>
            <button class="primary-btn" type="submit">Dodaj firmę</button>
          </form>
        </div>

        <div>
          <h2>Zapisane firmy</h2>
          <table v-if="companies.length" class="table">
            <thead>
              <tr>
                <th>NIP</th>
                <th>Nazwa</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="company in companies" :key="company.id">
                <td>{{ company.taxId }}</td>
                <td>{{ company.name }}</td>
                <td>
                  <button class="secondary-btn" type="button" @click="removeCompany(company.id)">
                    Usuń
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted">Brak zapisanych firm. Dodaj pierwszą po lewej.</p>
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

const companies = ref(dictionaryStore.cateringCompanies)
const form = reactive({
  taxId: '',
  name: ''
})
const errorMessage = ref('')
const successMessage = ref('')

function resetFeedback() {
  errorMessage.value = ''
  successMessage.value = ''
}

function addCompany() {
  resetFeedback()
  const taxId = form.taxId.trim()
  const name = form.name.trim()

  if (!taxId || !name) {
    errorMessage.value = 'Podaj zarówno NIP, jak i nazwę firmy.'
    return
  }

  dictionaryStore.addCateringCompany({ taxId, name })
  companies.value = dictionaryStore.cateringCompanies

  form.taxId = ''
  form.name = ''
  successMessage.value = 'Dodano firmę cateringową do słownika.'
}

function removeCompany(id: number) {
  dictionaryStore.removeCateringCompany(id)
  companies.value = dictionaryStore.cateringCompanies
}

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

onMounted(() => {
  userStore.hydrateFromStorage()
  dictionaryStore.hydrateFromStorage()
  companies.value = dictionaryStore.cateringCompanies

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
