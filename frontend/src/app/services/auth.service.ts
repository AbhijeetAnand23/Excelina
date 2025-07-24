import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private userSubject = new BehaviorSubject<string | null>(this.getUserName());
  user$ = this.userSubject.asObservable();

  getUserName(): string | null {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user?.name || null;
  }

  setUser(user: any) {
    localStorage.setItem('user', JSON.stringify(user));
    this.userSubject.next(user.name);
  }

  clearUser() {
    localStorage.removeItem('user');
    this.userSubject.next(null);
  }
}
