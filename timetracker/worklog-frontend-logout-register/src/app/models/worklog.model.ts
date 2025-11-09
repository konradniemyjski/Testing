export interface Worklog {
  id: number;
  workDate: string; // Use string for date, handle conversion as needed
  userId: number;
  userName?: string;
  userSurname?: string;
  timeSpent: number; // Use number, matches BigDecimal in backend DTO
  mealsOrdered: number;
  nightsSpent: number;
}

