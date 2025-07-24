import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Router } from '@angular/router';
import { ToastService } from '../../services/toast.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  error: string = '';

  constructor(private api: ApiService, private router: Router, private toast: ToastService, private auth: AuthService) {}

  login() {
    this.error = '';

    this.api.loginCandidate(this.email, this.password).subscribe({
      next: (res: any) => {
        localStorage.setItem('candidate_id', res.candidate_id);
        localStorage.setItem('user', JSON.stringify({ name: res.name, email: res.email }));
        localStorage.setItem('token', res.token);
        this.auth.setUser({ name: res.name, email: res.email });
        this.toast.show('success', res.message);
        this.router.navigate(['/home']); 
      },
      error: err => {
        this.toast.show('error', err.error?.error);
      }
    });
  }
}
