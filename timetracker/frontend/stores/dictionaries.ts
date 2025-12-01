import { defineStore } from 'pinia'
import { useApi } from '~/composables/useApi'

const STORAGE_KEY = 'worklog.dictionaries'

export type CateringCompany = {
  id: number
  tax_id: string
  name: string
}

export type AccommodationCompany = {
  id: number
  tax_id: string
  name: string
}

export type TeamMember = {
  id: number
  name: string
}

type DictionaryState = {
  cateringCompanies: CateringCompany[]
  accommodationCompanies: AccommodationCompany[]
  teamMembers: TeamMember[]
  loaded: boolean
}

export const useDictionaryStore = defineStore('dictionaries', {
  state: (): DictionaryState => ({
    cateringCompanies: [],
    accommodationCompanies: [],
    teamMembers: [],
    loaded: false
  }),
  actions: {
    hydrateFromStorage() {
      if (this.loaded || !process.client) {
        return
      }

      const cached = window.localStorage.getItem(STORAGE_KEY)
      if (!cached) {
        return
      }

      try {
        const parsed = JSON.parse(cached) as Omit<DictionaryState, 'loaded'>
        this.cateringCompanies = parsed.cateringCompanies
        this.accommodationCompanies = parsed.accommodationCompanies
        this.teamMembers = parsed.teamMembers
        this.loaded = true
      } catch {
        // ignore cache parsing issues and fall back to fetching
      }
    },
    async fetchDictionaries(force = false) {
      if (this.loaded && !force) {
        return
      }
      const api = useApi()
      const [catering, accommodation, team] = await Promise.all([
        api<CateringCompany[]>('/dictionaries/catering'),
        api<AccommodationCompany[]>('/dictionaries/accommodation'),
        api<TeamMember[]>('/dictionaries/team')
      ])
      this.cateringCompanies = catering
      this.accommodationCompanies = accommodation
      this.teamMembers = team
      this.loaded = true

      if (process.client) {
        const payload = {
          cateringCompanies: this.cateringCompanies,
          accommodationCompanies: this.accommodationCompanies,
          teamMembers: this.teamMembers
        }
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
      }
    },
    async createCateringCompany(payload: Omit<CateringCompany, 'id'>) {
      const api = useApi()
      const created = await api<CateringCompany>('/dictionaries/catering', {
        method: 'POST',
        body: payload
      })
      this.cateringCompanies = [...this.cateringCompanies, created]
      return created
    },
    async deleteCateringCompany(id: number) {
      const api = useApi()
      await api(`/dictionaries/catering/${id}`, { method: 'DELETE' })
      this.cateringCompanies = this.cateringCompanies.filter((company) => company.id !== id)
    },
    async updateCateringCompany(id: number, payload: Omit<CateringCompany, 'id'>) {
      const api = useApi()
      const updated = await api<CateringCompany>(`/dictionaries/catering/${id}`, {
        method: 'PUT',
        body: payload
      })
      this.cateringCompanies = this.cateringCompanies.map((company) =>
        company.id === id ? updated : company
      )
      return updated
    },
    async createAccommodationCompany(payload: Omit<AccommodationCompany, 'id'>) {
      const api = useApi()
      const created = await api<AccommodationCompany>('/dictionaries/accommodation', {
        method: 'POST',
        body: payload
      })
      this.accommodationCompanies = [...this.accommodationCompanies, created]
      return created
    },
    async deleteAccommodationCompany(id: number) {
      const api = useApi()
      await api(`/dictionaries/accommodation/${id}`, { method: 'DELETE' })
      this.accommodationCompanies = this.accommodationCompanies.filter((company) => company.id !== id)
    },
    async updateAccommodationCompany(id: number, payload: Omit<AccommodationCompany, 'id'>) {
      const api = useApi()
      const updated = await api<AccommodationCompany>(`/dictionaries/accommodation/${id}`, {
        method: 'PUT',
        body: payload
      })
      this.accommodationCompanies = this.accommodationCompanies.map((company) =>
        company.id === id ? updated : company
      )
      return updated
    },
    async createTeamMember(payload: Omit<TeamMember, 'id'>) {
      const api = useApi()
      const created = await api<TeamMember>('/dictionaries/team', {
        method: 'POST',
        body: payload
      })
      this.teamMembers = [...this.teamMembers, created]
      return created
    },
    async deleteTeamMember(id: number) {
      const api = useApi()
      await api(`/dictionaries/team/${id}`, { method: 'DELETE' })
      this.teamMembers = this.teamMembers.filter((member) => member.id !== id)
    }
  }
})
