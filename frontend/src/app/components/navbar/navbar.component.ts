import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit {
  userName: string | null = null;

  constructor(private router: Router, private auth: AuthService) {}

  ngOnInit(): void {
    this.auth.user$.subscribe(name => {
      this.userName = name ? name.split(' ')[0] : null;
    });
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('candidate_id');
  }

  logout(): void {
    localStorage.removeItem('candidate_id');
    this.auth.clearUser();
    this.router.navigate(['/login']).then(() => {
      location.reload(); 
    });
  }
}
