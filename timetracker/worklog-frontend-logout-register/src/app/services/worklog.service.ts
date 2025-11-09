import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Worklog } from '../models/worklog.model';

@Injectable({
  providedIn: 'root'
})
export class WorklogService {

  private apiUrl = 'http://localhost:8080/api/worklogs'; // Adjust if backend runs elsewhere

  constructor(private http: HttpClient) { }

  getWorklogs(userId?: number): Observable<Worklog[]> {
    let params = new HttpParams();
    if (userId) {
      params = params.set('userId', userId.toString());
    }
    return this.http.get<Worklog[]>(this.apiUrl, { params });
  }

  getWorklog(id: number): Observable<Worklog> {
    return this.http.get<Worklog>(`${this.apiUrl}/${id}`);
  }

  createWorklog(worklog: Omit<Worklog, 'id' | 'userName' | 'userSurname'>): Observable<Worklog> {
    return this.http.post<Worklog>(this.apiUrl, worklog);
  }

  updateWorklog(id: number, worklog: Omit<Worklog, 'id' | 'userName' | 'userSurname'>): Observable<Worklog> {
    return this.http.put<Worklog>(`${this.apiUrl}/${id}`, worklog);
  }

  deleteWorklog(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  // Add method for XLS export later (Step 7.2)
  downloadWorklogsXls(): Observable<Blob> {
      // The actual implementation will depend on the backend endpoint (Step 7.1)
      // For now, just a placeholder
      const exportUrl = `${this.apiUrl}/export/xls`; // Example URL
      return this.http.get(exportUrl, {
          responseType: 'blob' // Important: response type must be blob for file download
      });
  }
}

