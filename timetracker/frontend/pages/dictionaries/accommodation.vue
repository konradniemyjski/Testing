<template>
  <div v-if="ready" class="container">
    <MainNavigation :can-manage-users="canManageUsers" @logout="handleLogout" />
    <div class="card">
      <header class="page-header">
        <div>
          <h1>Administracja — firmy noclegowe</h1>
          <p class="text-muted">Dodaj NIP oraz nazwę firm zapewniających noclegi.</p>
        </div>
      </header>

      <section class="grid-section">
        <div>
          <h2>Dodaj firmę</h2>
          <form class="entry-form" @submit.prevent="addCompany">
            <div class="form-group">
              <label for="accommodationTaxId">NIP</label>
              <input
                id="accommodationTaxId"
                v-model="form.taxId"
                type="text"
                required
                placeholder="np. 987-654-32-10"
              />
            </div>
            <div class="form-group">
              <label for="accommodationName">Nazwa firmy</label>
              <input
                id="accommodationName"
                v-model="form.name"
                type="text"
                required
                placeholder="np. Hotelowa Przystań Sp. z o.o."
              />
            </div>
            <p v-if="errorMessage" class="feedback feedback--error">{{ errorMessage }}</p>
            <p v-if="successMessage" class="feedback feedback--success">{{ successMessage }}</p>
            <button class="primary-btn" type="submit" :disabled="submitting">
              {{ submitting ? 'Zapisywanie…' : 'Dodaj firmę' }}
            </button>
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
                <td>{{ company.tax_id }}</td>
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
import { useDictionaryStore } from '~/stores/dictionaries'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

const userStore = useUserStore()
const dictionaryStore = useDictionaryStore()
const router = useRouter()
const canManageUsers = computed(() => userStore.profile?.role === 'admin')
const isAdmin = computed(() => userStore.profile?.role === 'admin')
const nipPattern = /^((\d{3}[- ]\d{3}[- ]\d{2}[- ]\d{2})|(\d{3}[- ]\d{2}[- ]\d{2}[- ]\d{3}))$/

const companies = computed(() => dictionaryStore.accommodationCompanies)
const form = reactive({
  taxId: '',
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

async function addCompany() {
  resetFeedback()
  const taxId = form.taxId.trim()
  const name = form.name.trim()

  if (!taxId || !name) {
    errorMessage.value = 'Podaj zarówno NIP, jak i nazwę firmy.'
    return
  }

  if (!nipPattern.test(taxId)) {
    errorMessage.value = 'NIP musi być w formacie 123-456-78-90 lub 123-45-67-890.'
    return
  }

  try {
    submitting.value = true
    await dictionaryStore.createAccommodationCompany({ tax_id: taxId, name })
    form.taxId = ''
    form.name = ''
    successMessage.value = 'Dodano firmę noclegową do słownika.'
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'Nie udało się zapisać firmy.'
  } finally {
    submitting.value = false
  }
}

async function removeCompany(id: number) {
  await dictionaryStore.deleteAccommodationCompany(id)
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
