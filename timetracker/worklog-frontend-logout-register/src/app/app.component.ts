import { Component } from '@angular/core';
import { NgIf } from '@angular/common';
import { RouterLink, RouterOutlet } from '@angular/router';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [
    NgIf,          // żeby działało *ngIf
    RouterLink,    // żeby działało routerLink=""
    RouterOutlet   // żeby działało <router-outlet>
  ]
})
export class AppComponent {
  constructor(public auth: AuthService) {}
}
