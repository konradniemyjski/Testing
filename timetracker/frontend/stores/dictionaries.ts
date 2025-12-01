import { defineStore } from 'pinia'

export type CateringCompany = {
  id: number
  taxId: string
  name: string
}

export type AccommodationCompany = {
  id: number
  taxId: string
  name: string
}

export type TeamMember = {
  id: number
  name: string
}

const STORAGE_KEY = 'worklog.dictionaries'

type DictionaryState = {
  cateringCompanies: CateringCompany[]
  accommodationCompanies: AccommodationCompany[]
  teamMembers: TeamMember[]
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
}

export const useDictionaryStore = defineStore('dictionaries', {
  state: (): DictionaryState => ({
    cateringCompanies: [],
    accommodationCompanies: [],
    teamMembers: [],
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
    }
  }
})
