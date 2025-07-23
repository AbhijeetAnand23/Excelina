import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-feedback',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './feedback.component.html',
  styleUrls: ['./feedback.component.scss']
})
export class FeedbackComponent implements OnInit {
  candidateId = localStorage.getItem('candidate_id');
  status = '';
  totalScore: number | null = null;
  currentLevel: number | null = null;
  eliminatedLevel: number | null = null;
  progress: any[] = [];

  constructor(private api: ApiService, private router: Router) {}

  ngOnInit(): void {
    if (!this.candidateId) {
      this.router.navigate(['/login']);
      return;
    }

    this.api.getCandidateStatus().subscribe((res: any) => {
      this.status = res.status;
      this.totalScore = res.total_score;
      this.currentLevel = res.current_level;
      this.eliminatedLevel = res.eliminated_at_level;
    });

    this.api.getQuestions(this.candidateId).subscribe((res: any[]) => {
      this.progress = res.filter(q => q.score !== null);
    });
  }

  goToNextLevel() {
    this.router.navigate(['/home']);
  }

  goHome() {
    this.router.navigate(['/home']);
  }
}
