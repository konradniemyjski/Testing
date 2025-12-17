<template>
  <div>
    <table class="table">
      <thead>
        <tr>
          <th>Data</th>
          <th>Kod</th>
          <th>Projekt</th>
          <th>Pracownik</th>
          <th>Zespół</th>
          <th>Godziny</th>
          <th v-if="['catering', 'accommodation'].includes(type) || !type">Posiłki</th>
          <th v-if="['catering', 'accommodation'].includes(type) || !type">Noclegi</th>
          <th v-if="type === 'catering'">Firma Cateringowa</th>
          <th v-if="type === 'accommodation'">Firma Noclegowa</th>
          <th>Uwagi</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in data" :key="entry.id">
          <td>{{ formatDate(entry.date) }}</td>
          <td>{{ entry.site_code }}</td>
          <td>{{ entry.project?.name || '—' }}</td>
          <td>{{ formatWorker(entry) }}</td>
          <td>{{ entry.team_member?.team?.name || '—' }}</td>
          <td>{{ entry.hours_worked }}</td>
          <td v-if="['catering', 'accommodation'].includes(type) || !type">{{ entry.meals_served }}</td>
          <td v-if="['catering', 'accommodation'].includes(type) || !type">{{ entry.overnight_stays }}</td>
          <td v-if="type === 'catering'">{{ entry.catering_company?.name || '—' }}</td>
          <td v-if="type === 'accommodation'">{{ entry.accommodation_company?.name || '—' }}</td>
          <td>{{ entry.notes || '—' }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="pages > 1" class="pagination-controls">
      <button @click="$emit('page-change', 1)" :disabled="page === 1" class="pagination-btn">
        &lt;&lt;
      </button>
      <button @click="$emit('page-change', page - 1)" :disabled="page === 1" class="pagination-btn">
        &lt;
      </button>
      <span class="pagination-info">Strona {{ page }} z {{ pages }}</span>
      <button @click="$emit('page-change', page + 1)" :disabled="page === pages" class="pagination-btn">
        &gt;
      </button>
      <button @click="$emit('page-change', pages)" :disabled="page === pages" class="pagination-btn">
        &gt;&gt;
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  data: any[]
  total: number
  page: number
  pages: number
  type?: string // 'catering' | 'accommodation' | undefined
}>()

defineEmits<{
  (e: 'page-change', page: number): void
}>()

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('pl-PL')
}

function formatWorker(entry: any) {
  if (entry.team_member) return entry.team_member.name
  if (entry.user) return entry.user.full_name || entry.user.email
  return '—'
}
</script>

<style scoped>
/* Reuse table styles from global or copied here */
.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.table th,
.table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.table th {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.pagination-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f3f3f3;
}

.pagination-info {
  font-weight: 500;
  margin: 0 0.5rem;
}
</style>
