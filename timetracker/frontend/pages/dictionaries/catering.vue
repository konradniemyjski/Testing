<template>
  <div v-if="ready" class="container">
    <MainNavigation :can-manage-users="canManageUsers" @logout="handleLogout" />
    <div class="card">
      <header class="page-header">
        <div>
          <h1>Administracja — firmy cateringowe</h1>
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
                <td>
                  <template v-if="editingCompanyId === company.id">
                    <input
                      v-model="editForm.taxId"
                      type="text"
                      required
                      placeholder="np. 123-456-78-90"
                    />
                  </template>
                  <template v-else>
                    {{ company.tax_id }}
                  </template>
                </td>
                <td>
                  <template v-if="editingCompanyId === company.id">
                    <input
                      v-model="editForm.name"
                      type="text"
                      required
                      placeholder="np. Smaczny Catering Sp. z o.o."
                    />
                  </template>
                  <template v-else>
                    {{ company.name }}
                  </template>
                </td>
                <td>
                  <template v-if="editingCompanyId === company.id">
                    <button class="primary-btn" type="button" :disabled="editSubmitting" @click="saveCompany(company.id)">
                      {{ editSubmitting ? 'Zapisywanie…' : 'Zapisz' }}
                    </button>
                    <button class="secondary-btn" type="button" :disabled="editSubmitting" @click="cancelEdit">
                      Anuluj
                    </button>
                  </template>
                  <template v-else>
                    <button class="secondary-btn" type="button" @click="startEdit(company)">
                      Edytuj
                    </button>
                    <button class="secondary-btn" type="button" @click="removeCompany(company.id)">
                      Usuń
                    </button>
                  </template>
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
import { useDictionaryStore, type CateringCompany } from '~/stores/dictionaries'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

const userStore = useUserStore()
const dictionaryStore = useDictionaryStore()
const router = useRouter()
const canManageUsers = computed(() => userStore.profile?.role === 'admin')
const isAdmin = computed(() => userStore.profile?.role === 'admin')
const nipPattern = /^((\d{3}[- ]\d{3}[- ]\d{2}[- ]\d{2})|(\d{3}[- ]\d{2}[- ]\d{2}[- ]\d{3}))$/

const companies = computed(() => dictionaryStore.cateringCompanies)
const form = reactive({
  taxId: '',
  name: ''
})
const editForm = reactive({
  taxId: '',
  name: ''
})
const errorMessage = ref('')
const successMessage = ref('')
const submitting = ref(false)
const editSubmitting = ref(false)
const ready = ref(false)
const editingCompanyId = ref<number | null>(null)

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
    await dictionaryStore.createCateringCompany({ tax_id: taxId, name })
    form.taxId = ''
    form.name = ''
    successMessage.value = 'Dodano firmę cateringową do słownika.'
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'Nie udało się zapisać firmy.'
  } finally {
    submitting.value = false
  }
}

async function removeCompany(id: number) {
  await dictionaryStore.deleteCateringCompany(id)
}

function startEdit(company: CateringCompany) {
  resetFeedback()
  editingCompanyId.value = company.id
  editForm.taxId = company.tax_id
  editForm.name = company.name
}

function cancelEdit() {
  editingCompanyId.value = null
  editForm.taxId = ''
  editForm.name = ''
}

async function saveCompany(id: number) {
  resetFeedback()
  const taxId = editForm.taxId.trim()
  const name = editForm.name.trim()

  if (!taxId || !name) {
    errorMessage.value = 'Podaj zarówno NIP, jak i nazwę firmy.'
    return
  }

  if (!nipPattern.test(taxId)) {
    errorMessage.value = 'NIP musi być w formacie 123-456-78-90 lub 123-45-67-890.'
    return
  }

  try {
    editSubmitting.value = true
    await dictionaryStore.updateCateringCompany(id, { tax_id: taxId, name })
    successMessage.value = 'Zaktualizowano firmę cateringową.'
    cancelEdit()
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'Nie udało się zaktualizować firmy.'
  } finally {
    editSubmitting.value = false
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
