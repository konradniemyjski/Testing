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
          <h1>Słowniki firm i zespołu</h1>
=======
          <h1>Administracja</h1>
>>>>>>> theirs
          <p class="text-muted">
            Dodaj lub uzupełnij podstawowe dane wykorzystywane podczas rozliczeń i raportowania.
          </p>
        </div>
      </header>

      <section class="dictionary-grid">
        <div class="dictionary-tile">
          <div>
            <p class="tile-label">Firmy</p>
            <h2>Firmy cateringowe</h2>
            <p class="text-muted">Zapisz NIP oraz nazwę firmy obsługującej posiłki na budowie.</p>
          </div>
          <NuxtLink class="primary-btn" to="/dictionaries/catering">Przejdź do słownika</NuxtLink>
        </div>

        <div class="dictionary-tile">
          <div>
            <p class="tile-label">Firmy</p>
            <h2>Firmy noclegowe</h2>
            <p class="text-muted">Wprowadź NIP i nazwę firmy oferującej zakwaterowanie.</p>
          </div>
          <NuxtLink class="primary-btn" to="/dictionaries/accommodation">Przejdź do słownika</NuxtLink>
        </div>

        <div class="dictionary-tile">
          <div>
            <p class="tile-label">Zespół</p>
            <h2>Członkowie zespołu</h2>
            <p class="text-muted">Utwórz listę imion i nazwisk osób pracujących przy projekcie.</p>
          </div>
          <NuxtLink class="primary-btn" to="/dictionaries/team">Przejdź do słownika</NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
<<<<<<< ours
import { computed, onMounted } from 'vue'
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()
const router = useRouter()

const canManageUsers = computed(() => userStore.profile?.role === 'admin')
=======
import { computed, onMounted, ref } from 'vue'
import { useUserStore } from '~/stores/user'

definePageMeta({ ssr: false })

const userStore = useUserStore()
const router = useRouter()
const ready = ref(false)

const canManageUsers = computed(() => userStore.profile?.role === 'admin')
const isAdmin = computed(() => userStore.profile?.role === 'admin')
>>>>>>> theirs

function handleLogout() {
  userStore.clear()
  router.replace('/login')
}

onMounted(() => {
  userStore.hydrateFromStorage()
  if (!userStore.isAuthenticated) {
    router.replace('/login')
<<<<<<< ours
  }
=======
    return
  }

  if (!isAdmin.value) {
    router.replace('/dashboard')
    return
  }
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

.dictionary-grid {
  margin-top: 2rem;
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.dictionary-tile {
  display: grid;
  gap: 0.75rem;
  padding: 1.25rem;
  border: 1px solid rgba(37, 99, 235, 0.18);
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.06), rgba(124, 58, 237, 0.06));
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
}

.tile-label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
  font-weight: 600;
  font-size: 0.85rem;
}

@media (prefers-color-scheme: dark) {
  .dictionary-tile {
    border-color: rgba(96, 165, 250, 0.35);
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(124, 58, 237, 0.12));
    box-shadow: 0 12px 32px rgba(2, 6, 23, 0.55);
  }

  .tile-label {
    background: rgba(37, 99, 235, 0.24);
    color: #bfdbfe;
  }
}
</style>
