import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private apiUrl = 'http://localhost:8080/api/users'; // Adjust if backend runs elsewhere

  constructor(private http: HttpClient) { }

  getUsers(teamId?: number): Observable<User[]> {
    let params = new HttpParams();
    if (teamId) {
      params = params.set('teamId', teamId.toString());
    }
    return this.http.get<User[]>(this.apiUrl, { params });
  }

  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`);
  }

  createUser(user: Omit<User, 'id' | 'teamName'>): Observable<User> {
    return this.http.post<User>(this.apiUrl, user);
  }

  updateUser(id: number, user: Omit<User, 'id' | 'teamName'>): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${id}`, user);
  }

  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}

