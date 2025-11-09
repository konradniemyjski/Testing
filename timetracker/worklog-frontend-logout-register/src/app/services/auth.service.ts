import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

interface LoginResponse {
  token: string;
  role: string; // "ROLE_ADMIN" lub "ROLE_USER"
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = 'http://localhost:8080/api/auth';

  isLoggedIn = signal<boolean>(false);
  username = signal<string | null>(null);
  role = signal<string | null>(null);

  constructor(private http: HttpClient, private router: Router) {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('username');
    const storedRole = localStorage.getItem('role');
    if (token && storedUser) {
      this.isLoggedIn.set(true);
      this.username.set(storedUser);
      this.role.set(storedRole);
    }
  }

  login(username: string, password: string) {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, { username, password });
  }

  handleLoginSuccess(username: string, resp: LoginResponse) {
    localStorage.setItem('token', resp.token);
    localStorage.setItem('username', username);
    localStorage.setItem('role', resp.role);

    this.isLoggedIn.set(true);
    this.username.set(username);
    this.role.set(resp.role);

    this.router.navigate(['/worklogs']);
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');

    this.isLoggedIn.set(false);
    this.username.set(null);
    this.role.set(null);

    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  isAdmin(): boolean {
    return this.role() === 'ROLE_ADMIN';
  }
}
