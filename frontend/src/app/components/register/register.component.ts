import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { ToastService } from '../../services/toast.service';

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
    role: 'fresher',
    password: ''
  };


  constructor(private api: ApiService, private router: Router, private toast: ToastService) {}

  onSubmit() {

    this.api.registerCandidate(this.candidate).subscribe({
      next: (res: any) => {
        this.toast.show('success', res.message);
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 1000);
      },
      error: (err) => {
        this.toast.show('error', err.error?.error);
      }
    });
  }
}
