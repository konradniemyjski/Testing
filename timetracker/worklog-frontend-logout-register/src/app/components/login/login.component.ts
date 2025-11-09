import { Component, signal } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, NgIf],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username = '';
  password = '';

  loading = signal(false);
  error = signal<string | null>(null);

  constructor(public auth: AuthService, private router: Router) {
    // jeśli już zalogowany -> od razu przenieś np. na /worklogs
    if (this.auth.isLoggedIn()) {
      this.router.navigate(['/worklogs']);
    }
  }

  submit() {
    this.loading.set(true);
    this.error.set(null);

    this.auth.login(this.username, this.password).subscribe({
      next: resp => {
        this.loading.set(false);
        this.auth.handleLoginSuccess(this.username, resp);
        // handleLoginSuccess robi navigate(['/worklogs'])
      },
      error: _ => {
        this.loading.set(false);
        this.error.set('Nieprawidłowe dane logowania');
      }
    });
  }
}
