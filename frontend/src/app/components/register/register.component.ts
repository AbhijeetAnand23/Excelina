import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  candidate = {
    name: '',
    email: '',
    role: 'beginner',
    password: ''
  };

  error = '';
  success = '';

  constructor(private api: ApiService, private router: Router) {}

  onSubmit() {
    this.error = '';
    this.success = '';

    this.api.registerCandidate(this.candidate).subscribe({
      next: (res: any) => {
        this.success = 'Registration successful! Please log in.';
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 1000);
      },
      error: (err) => {
        this.error = err.error.error || 'Registration failed.';
      }
    });
  }
}
