export interface User {
  id: number;
  name: string;
  surname: string;
  teamId: number;
  teamName?: string; // Optional, based on backend DTO
}

