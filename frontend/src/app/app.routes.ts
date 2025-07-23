import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  {
    path: 'register',
    loadComponent: () =>
      import('./components/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'login',
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'interview',
    loadComponent: () =>
      import('./components/interview/interview.component').then(m => m.InterviewComponent),
    canActivate: [authGuard]
  },
  {
    path: 'feedback',
    loadComponent: () =>
      import('./components/feedback/feedback.component').then(m => m.FeedbackComponent),
    canActivate: [authGuard]
  },
];
