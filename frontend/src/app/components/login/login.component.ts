import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Router } from '@angular/router';

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

  constructor(private api: ApiService, private router: Router) {}

  login() {
    this.error = '';

    this.api.loginCandidate(this.email, this.password).subscribe({
      next: (res: any) => {
        localStorage.setItem('candidate_id', res.candidate_id);
        localStorage.setItem('token', res.token);

        if (res.status === 'in_progress') {
          this.router.navigate(['/interview']);
        } else {
          this.router.navigate(['/feedback']);
        }
      },
      error: err => {
        this.error = err.error?.error || 'Login failed';
      }
    });
  }
}
