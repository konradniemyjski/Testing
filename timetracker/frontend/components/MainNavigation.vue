<template>
  <nav class="main-nav">
    <div class="main-nav__links">
      <button
        type="button"
        class="nav-btn"
        :class="{ 'nav-btn--active': isActive('/dashboard') }"
        @click="navigate('/dashboard')"
      >
        Logowanie czasu
      </button>
      <button
        type="button"
        class="nav-btn"
        :class="{ 'nav-btn--active': isActive('/projects') }"
        @click="navigate('/projects')"
      >
        Zarządzaj budowami
      </button>
      <button
        v-if="canManageUsers"
        type="button"
        class="nav-btn"
        :class="{ 'nav-btn--active': isActive('/users') }"
        @click="navigate('/users')"
      >
        Użytkownicy
      </button>
    </div>
    <div class="main-nav__actions">
      <button
        v-if="userStore.profile"
        type="button"
        class="nav-btn nav-btn--profile"
        @click="openProfileModal"
      >
        <span class="nav-profile__avatar">{{ profileInitials }}</span>
        <span class="nav-profile__details">
          <span class="nav-profile__name">{{ displayName }}</span>
          <span class="nav-profile__email">{{ profileEmail }}</span>
        </span>
      </button>
      <button type="button" class="nav-btn nav-btn--logout" @click="emit('logout')">
        Wyloguj
      </button>
    </div>

    <Teleport to="body">
      <div v-if="showProfileModal" class="profile-modal__backdrop" @click="closeProfileModal">
        <div class="profile-modal__dialog" @click.stop>
          <header class="profile-modal__header">
            <div>
              <h2>Zarządzanie profilem</h2>
              <p>Zmień swój login, nazwę wyświetlaną lub hasło.</p>
            </div>
            <button
              type="button"
              class="profile-modal__close"
              aria-label="Zamknij okno"
              @click="closeProfileModal"
            >
              ×
            </button>
          </header>

          <form class="profile-modal__form" @submit.prevent="submitProfileUpdate">
            <div class="form-group">
              <label for="profileEmail">E-mail (login)</label>
              <input
                id="profileEmail"
                v-model="profileForm.email"
                type="email"
                required
                placeholder="np. jan.kowalski@example.com"
              />
            </div>

            <div class="form-group">
              <label for="profileName">Nazwa wyświetlana</label>
              <input
                id="profileName"
                v-model="profileForm.full_name"
                type="text"
                placeholder="np. Jan Kowalski"
              />
              <p class="profile-modal__hint">Pozostaw puste, aby używać adresu e-mail.</p>
            </div>

            <div class="form-group">
              <label for="profilePassword">Nowe hasło</label>
              <input
                id="profilePassword"
                v-model="profileForm.password"
                type="password"
                placeholder="Wpisz nowe hasło (opcjonalne)"
                minlength="6"
              />
            </div>

            <div class="form-group">
              <label for="profileCurrentPassword">Obecne hasło</label>
              <input
                id="profileCurrentPassword"
                v-model="profileForm.current_password"
                type="password"
                :required="Boolean(profileForm.password)"
                placeholder="Wymagane przy zmianie hasła"
                minlength="6"
              />
            </div>

            <p v-if="profileError" class="profile-modal__feedback profile-modal__feedback--error">
              {{ profileError }}
            </p>
            <p v-if="profileSuccess" class="profile-modal__feedback profile-modal__feedback--success">
              {{ profileSuccess }}
            </p>

            <div class="profile-modal__actions">
              <button type="button" class="nav-btn nav-btn--secondary" @click="closeProfileModal">
                Anuluj
              </button>
              <button class="primary-btn" type="submit" :disabled="profileSaving">
                {{ profileSaving ? 'Zapisywanie…' : 'Zapisz zmiany' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </nav>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useUserStore, type UserProfile } from '~/stores/user'

const emit = defineEmits<{ (e: 'logout'): void }>()

const router = useRouter()
const route = useRoute()
const api = useApi()
const userStore = useUserStore()

if (import.meta.client && !userStore.hydrated) {
  userStore.hydrateFromStorage()
}

const showProfileModal = ref(false)
const profileSaving = ref(false)
const profileError = ref('')
const profileSuccess = ref('')

const profileForm = reactive({
  email: '',
  full_name: '',
  password: '',
  current_password: ''
})

const canManageUsers = computed(() => userStore.profile?.role === 'admin')
const displayName = computed(
  () => userStore.profile?.full_name?.trim() || userStore.profile?.email || 'Mój profil'
)
const profileEmail = computed(() => userStore.profile?.email || '')
const profileInitials = computed(() => {
  const name = userStore.profile?.full_name?.trim()
  if (name) {
    const initials = name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? '')
      .join('')
    return initials || name.slice(0, 2).toUpperCase()
  }
  const email = userStore.profile?.email ?? ''
  return email.slice(0, 2).toUpperCase() || 'UŻ'
})

function navigate(path: string) {
  if (route.path !== path) {
    router.push(path)
  }
}

function isActive(path: string) {
  return route.path === path
}

function openProfileModal() {
  showProfileModal.value = true
}

function closeProfileModal() {
  showProfileModal.value = false
  profileError.value = ''
  profileSuccess.value = ''
}

watch(showProfileModal, (open) => {
  if (open) {
    profileForm.email = userStore.profile?.email ?? ''
    profileForm.full_name = userStore.profile?.full_name ?? ''
    profileForm.password = ''
    profileForm.current_password = ''
    profileError.value = ''
    profileSuccess.value = ''
  }
})

async function submitProfileUpdate() {
  profileError.value = ''
  profileSuccess.value = ''

  if (!userStore.profile) {
    profileError.value = 'Brak danych profilu użytkownika.'
    return
  }

  const payload: Record<string, string | null> = {}
  const trimmedEmail = profileForm.email.trim()
  if (trimmedEmail && trimmedEmail !== userStore.profile.email) {
    payload.email = trimmedEmail
  }

  const trimmedFullName = profileForm.full_name.trim()
  const currentFullName = (userStore.profile.full_name ?? '').trim()
  if (trimmedFullName !== currentFullName) {
    payload.full_name = trimmedFullName ? trimmedFullName : null
  }

  if (profileForm.password) {
    if (!profileForm.current_password) {
      profileError.value = 'Podaj obecne hasło, aby ustawić nowe hasło.'
      return
    }
    payload.password = profileForm.password
    payload.current_password = profileForm.current_password
  }

  if (!Object.keys(payload).length) {
    profileSuccess.value = 'Brak zmian do zapisania.'
    profileForm.password = ''
    profileForm.current_password = ''
    return
  }

  try {
    profileSaving.value = true
    const updatedProfile = await api<UserProfile>('/auth/me', {
      method: 'PUT',
      body: payload
    })
    userStore.updateProfile(updatedProfile)
    profileSuccess.value = 'Profil został zaktualizowany.'
    profileForm.password = ''
    profileForm.current_password = ''
  } catch (error: any) {
    profileError.value =
      error?.data?.detail || 'Nie udało się zapisać zmian. Spróbuj ponownie.'
  } finally {
    profileSaving.value = false
  }
}
</script>

<style scoped>
.main-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.75rem;
  padding: 0.75rem 1rem;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(124, 58, 237, 0.12));
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.main-nav__links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.main-nav__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav-btn {
  border: none;
  border-radius: 999px;
  padding: 0.6rem 1.5rem;
  font-weight: 600;
  font-size: 0.95rem;
  color: #1f2937;
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 10px 18px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.nav-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 28px rgba(37, 99, 235, 0.2);
}

.nav-btn--active {
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
}

.nav-btn--profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.9);
}

.nav-btn--logout {
  color: #fff;
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.nav-btn--secondary {
  background: rgba(148, 163, 184, 0.2);
  color: #1f2937;
}

.nav-profile__avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(124, 58, 237, 0.25));
  color: #1d4ed8;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.nav-profile__details {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.nav-profile__name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #1f2937;
}

.nav-profile__email {
  font-size: 0.8rem;
  color: #6b7280;
}

.profile-modal__backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 50;
}

.profile-modal__dialog {
  width: min(480px, 100%);
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.25);
  padding: 1.75rem;
}

.profile-modal__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.profile-modal__header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.profile-modal__header p {
  margin: 0.35rem 0 0;
  color: #6b7280;
}

.profile-modal__close {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: #64748b;
}

.profile-modal__form {
  display: grid;
  gap: 1rem;
}

.profile-modal__hint {
  margin: 0;
  font-size: 0.8rem;
  color: #9ca3af;
}

.profile-modal__feedback {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.profile-modal__feedback--error {
  color: #ef4444;
}

.profile-modal__feedback--success {
  color: #10b981;
}

.profile-modal__actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

@media (prefers-color-scheme: dark) {
  .main-nav {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(124, 58, 237, 0.18));
    border-color: rgba(96, 165, 250, 0.28);
    box-shadow: 0 20px 40px rgba(2, 6, 23, 0.6);
  }

  .nav-btn {
    color: #e2e8f0;
    background: rgba(15, 23, 42, 0.65);
    box-shadow: 0 12px 30px rgba(2, 6, 23, 0.4);
  }

  .nav-btn:hover {
    box-shadow: 0 18px 36px rgba(59, 130, 246, 0.35);
  }

  .nav-btn--active {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.85), rgba(124, 58, 237, 0.85));
  }

  .nav-btn--profile {
    background: rgba(15, 23, 42, 0.7);
  }

  .nav-btn--logout {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.85), rgba(249, 115, 22, 0.85));
  }

  .nav-btn--secondary {
    background: rgba(148, 163, 184, 0.18);
    color: #e2e8f0;
  }

  .nav-profile__avatar {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.35), rgba(124, 58, 237, 0.4));
    color: #bfdbfe;
  }

  .nav-profile__name {
    color: #e2e8f0;
  }

  .nav-profile__email {
    color: #94a3b8;
  }

  .profile-modal__dialog {
    background: rgba(15, 23, 42, 0.95);
    box-shadow: 0 28px 60px rgba(2, 6, 23, 0.75);
  }

  .profile-modal__header p,
  .profile-modal__hint {
    color: #94a3b8;
  }

  .profile-modal__close {
    color: #cbd5f5;
  }
}
</style>
