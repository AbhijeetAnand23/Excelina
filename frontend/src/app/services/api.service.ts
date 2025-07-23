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

  registerCandidate(data: any) {
    return this.http.post(`${this.baseUrl}/register-candidate`, data);
  }

  getQuestions(candidateId: string) {
    return this.http.get(`${this.baseUrl}/get-questions/${candidateId}`);
  }

  submitAnswer(payload: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/submit-answer`, payload, {
      headers: this.getAuthHeaders()
    });
  }

  nextLevel(candidateId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/next-level`, { candidate_id: candidateId }, {
      headers: this.getAuthHeaders()
    });
  }

  getCandidateStatus(candidateId: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/candidate-status/${candidateId}`, {
      headers: this.getAuthHeaders()
    });
  }
  
  loginCandidate(email: string, password: string) {
    return this.http.post(`${this.baseUrl}/login-candidate`, { email, password });
  }
}
