import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { WorklogComponent } from './components/worklog/worklog.component';
import { TeamComponent } from './components/team/team.component';
import { UserComponent } from './components/user/user.component';
import { AdminGuard } from './guards/admin.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: '', redirectTo: 'worklogs', pathMatch: 'full' },
  { path: 'worklogs', component: WorklogComponent },
  { path: 'teams', component: TeamComponent, canActivate: [AdminGuard] },
  { path: 'users', component: UserComponent, canActivate: [AdminGuard] },
  { path: '**', redirectTo: 'worklogs' }
];
