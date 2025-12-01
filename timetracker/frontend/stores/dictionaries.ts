import { defineStore } from 'pinia'
<<<<<<< ours

export type CateringCompany = {
  id: number
  taxId: string
=======
import { useApi } from '~/composables/useApi'

export type CateringCompany = {
  id: number
  tax_id: string
>>>>>>> theirs
  name: string
}

export type AccommodationCompany = {
  id: number
<<<<<<< ours
  taxId: string
=======
  tax_id: string
>>>>>>> theirs
  name: string
}

export type TeamMember = {
  id: number
  name: string
}

<<<<<<< ours
const STORAGE_KEY = 'worklog.dictionaries'

=======
>>>>>>> theirs
type DictionaryState = {
  cateringCompanies: CateringCompany[]
  accommodationCompanies: AccommodationCompany[]
  teamMembers: TeamMember[]
<<<<<<< ours
  hydrated: boolean
}

function persistState(state: DictionaryState) {
  if (!process.client) return
  const payload = JSON.stringify({
    cateringCompanies: state.cateringCompanies,
    accommodationCompanies: state.accommodationCompanies,
    teamMembers: state.teamMembers
  })
  window.localStorage.setItem(STORAGE_KEY, payload)
=======
  loaded: boolean
>>>>>>> theirs
}

export const useDictionaryStore = defineStore('dictionaries', {
  state: (): DictionaryState => ({
    cateringCompanies: [],
    accommodationCompanies: [],
    teamMembers: [],
<<<<<<< ours
    hydrated: false
  }),
  actions: {
    hydrateFromStorage() {
      if (this.hydrated || !process.client) {
        return
      }

      const stored = window.localStorage.getItem(STORAGE_KEY)
      if (stored) {
        try {
          const parsed = JSON.parse(stored) as Partial<DictionaryState>
          this.cateringCompanies = parsed.cateringCompanies ?? []
          this.accommodationCompanies = parsed.accommodationCompanies ?? []
          this.teamMembers = parsed.teamMembers ?? []
        } catch {
          this.cateringCompanies = []
          this.accommodationCompanies = []
          this.teamMembers = []
        }
      }

      this.hydrated = true
    },
    addCateringCompany(company: Omit<CateringCompany, 'id'>) {
      const entry = { ...company, id: Date.now() }
      this.cateringCompanies.push(entry)
      persistState(this)
      return entry
    },
    removeCateringCompany(id: number) {
      this.cateringCompanies = this.cateringCompanies.filter((company) => company.id !== id)
      persistState(this)
    },
    addAccommodationCompany(company: Omit<AccommodationCompany, 'id'>) {
      const entry = { ...company, id: Date.now() }
      this.accommodationCompanies.push(entry)
      persistState(this)
      return entry
    },
    removeAccommodationCompany(id: number) {
      this.accommodationCompanies = this.accommodationCompanies.filter((company) => company.id !== id)
      persistState(this)
    },
    addTeamMember(member: Omit<TeamMember, 'id'>) {
      const entry = { ...member, id: Date.now() }
      this.teamMembers.push(entry)
      persistState(this)
      return entry
    },
    removeTeamMember(id: number) {
      this.teamMembers = this.teamMembers.filter((member) => member.id !== id)
      persistState(this)
=======
    loaded: false
  }),
  actions: {
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
>>>>>>> theirs
    }
  }
})
