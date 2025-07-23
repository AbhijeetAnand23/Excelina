import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  // ✅ Registration
  registerCandidate(data: any) {
    return this.http.post(`${this.baseUrl}/register-candidate`, data);
  }

  // ✅ Login
  loginCandidate(email: string, password: string) {
    return this.http.post(`${this.baseUrl}/login-candidate`, { email, password });
  }

  // ✅ Get Questions
  getQuestions(candidateId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/get-questions/${candidateId}`);
  }

  // ✅ Submit Answer
  submitAnswer(payload: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/submit-answer`, payload, {
      headers: this.getAuthHeaders()
    });
  }

  // ✅ Start a new round (Level)
  startRound(data: { round: number; level: number }): Observable<any> {
    return this.http.post(`${this.baseUrl}/start-round`, data, {
      headers: this.getAuthHeaders()
    });
  }

  // ✅ Complete and evaluate current round
  completeRound(): Observable<any> {
    return this.http.post(`${this.baseUrl}/complete-round`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  // ✅ Get Candidate Status
  getCandidateStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/candidate-status`, {
      headers: this.getAuthHeaders()
    });
  }

  getLastRoundStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/last-round-status`, {
      headers: this.getAuthHeaders()
    });
  }
}
