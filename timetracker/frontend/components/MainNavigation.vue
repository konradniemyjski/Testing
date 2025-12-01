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
        v-if="userStore.profile?.role === 'admin'"
        type="button"
        class="nav-btn"
        :class="{ 'nav-btn--active': isActive('/dictionaries') }"
        @click="navigate('/dictionaries')"
      >
        Administracja
      </button>
      <button
        v-if="userStore.profile?.role === 'admin'"
        type="button"
        class="nav-btn"
        :class="{ 'nav-btn--active': isActive('/users') }"
        @click="navigate('/users')"
      >
        Użytkownicy
      </button>
    </div>
    <button type="button" class="nav-btn nav-btn--logout" @click="emit('logout')">
      Wyloguj
    </button>
  </nav>
</template>


<script setup lang="ts">
import { useUserStore } from '~/stores/user'

const emit = defineEmits<{ (e: 'logout'): void }>()

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

function navigate(path: string) {
  if (route.path !== path) {
    router.push(path)
  }
}

function isActive(path: string) {
  return route.path === path || route.path.startsWith(`${path}/`)
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
  cursor: pointer;
}

.nav-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 28px rgba(37, 99, 235, 0.2);
}

.nav-btn--active {
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
}

.nav-btn--logout {
  color: #fff;
  background: linear-gradient(135deg, #ef4444, #f97316);
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

  .nav-btn--logout {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.85), rgba(249, 115, 22, 0.85));
  }
}
</style>
