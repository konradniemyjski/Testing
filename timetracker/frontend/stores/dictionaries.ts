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

export type TeamMemberRole = 'Pracownik' | 'Brygadzista'

export type TeamMember = {
  id: number
  name: string
  role: TeamMemberRole
  team_id: number | null
}

export type Team = {
  id: number
  name: string
  members: TeamMember[]
}

type DictionaryState = {
  cateringCompanies: CateringCompany[]
  accommodationCompanies: AccommodationCompany[]
  teams: Team[]
  teamMembers: TeamMember[]
  loaded: boolean
}

export const useDictionaryStore = defineStore('dictionaries', {
  state: (): DictionaryState => ({
    cateringCompanies: [],
    accommodationCompanies: [],
    teams: [],
    teamMembers: [],
    loaded: false
  }),
  actions: {
    refreshTeamMembers() {
      const aggregated = this.teams.flatMap((team) =>
        (team.members || []).map((member) => ({ ...member, team_id: team.id }))
      )
      this.teamMembers = aggregated.sort((a, b) => a.name.localeCompare(b.name, 'pl'))
    },
    persistState() {
      if (!process.client) {
        return
      }

      const payload = {
        cateringCompanies: this.cateringCompanies,
        accommodationCompanies: this.accommodationCompanies,
        teams: this.teams,
        teamMembers: this.teamMembers
      }
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    },
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
        this.teams = parsed.teams || []
        this.teamMembers = parsed.teamMembers || []
        this.refreshTeamMembers()
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
      const [catering, accommodation, teams] = await Promise.all([
        api<CateringCompany[]>('/dictionaries/catering'),
        api<AccommodationCompany[]>('/dictionaries/accommodation'),
        api<Team[]>('/dictionaries/team')
      ])
      this.cateringCompanies = catering
      this.accommodationCompanies = accommodation
      this.teams = teams
      this.refreshTeamMembers()
      this.loaded = true

      this.persistState()
    },
    async createCateringCompany(payload: Omit<CateringCompany, 'id'>) {
      const api = useApi()
      const created = await api<CateringCompany>('/dictionaries/catering', {
        method: 'POST',
        body: payload
      })
      this.cateringCompanies = [...this.cateringCompanies, created]
      this.persistState()
      return created
    },
    async deleteCateringCompany(id: number) {
      const api = useApi()
      await api(`/dictionaries/catering/${id}`, { method: 'DELETE' })
      this.cateringCompanies = this.cateringCompanies.filter((company) => company.id !== id)
      this.persistState()
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
      this.persistState()
      return updated
    },
    async createAccommodationCompany(payload: Omit<AccommodationCompany, 'id'>) {
      const api = useApi()
      const created = await api<AccommodationCompany>('/dictionaries/accommodation', {
        method: 'POST',
        body: payload
      })
      this.accommodationCompanies = [...this.accommodationCompanies, created]
      this.persistState()
      return created
    },
    async deleteAccommodationCompany(id: number) {
      const api = useApi()
      await api(`/dictionaries/accommodation/${id}`, { method: 'DELETE' })
      this.accommodationCompanies = this.accommodationCompanies.filter((company) => company.id !== id)
      this.persistState()
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
      this.persistState()
      return updated
    },
    async createTeam(name: string) {
      const api = useApi()
      const created = await api<Team>('/dictionaries/team', {
        method: 'POST',
        body: { name }
      })
      this.teams = [...this.teams, created]
      this.refreshTeamMembers()
      this.persistState()
      return created
    },
    async updateTeam(id: number, name: string) {
      const api = useApi()
      const updated = await api<Team>(`/dictionaries/team/${id}`, {
        method: 'PUT',
        body: { name }
      })
      this.teams = this.teams.map((team) => (team.id === id ? { ...updated } : team))
      this.refreshTeamMembers()
      this.persistState()
      return updated
    },
    async createTeamMember(payload: Omit<TeamMember, 'id'>) {
      const api = useApi()
      const created = await api<TeamMember>('/dictionaries/team/members', {
        method: 'POST',
        body: payload
      })
      this.teams = this.teams.map((team) =>
        team.id === created.team_id ? { ...team, members: [...team.members, created] } : team
      )
      const hasTargetTeam = this.teams.some((team) => team.id === created.team_id)
      if (!hasTargetTeam && created.team_id != null) {
        this.teams = [...this.teams, { id: created.team_id, name: '', members: [created] }]
      }
      this.refreshTeamMembers()
      this.persistState()
      return created
    },
    async updateTeamMember(id: number, payload: Omit<TeamMember, 'id'>) {
      const api = useApi()
      const updated = await api<TeamMember>(`/dictionaries/team/members/${id}`, {
        method: 'PUT',
        body: payload
      })
      this.teams = this.teams.map((team) => {
        const filteredMembers = team.members.filter((member) => member.id !== id)
        const shouldInclude = updated.team_id === team.id
        return shouldInclude
          ? { ...team, members: [...filteredMembers, updated] }
          : { ...team, members: filteredMembers }
      })
      const hasTargetTeam = this.teams.some((team) => team.id === updated.team_id)
      if (!hasTargetTeam && updated.team_id != null) {
        this.teams = [...this.teams, { id: updated.team_id, name: '', members: [updated] }]
      }
      this.refreshTeamMembers()
      this.persistState()
      return updated
    },
    async deleteTeamMember(id: number) {
      const api = useApi()
      await api(`/dictionaries/team/members/${id}`, { method: 'DELETE' })
      this.teams = this.teams.map((team) => ({
        ...team,
        members: team.members.filter((member) => member.id !== id)
      }))
      this.refreshTeamMembers()
      this.persistState()
    }
  }
})
