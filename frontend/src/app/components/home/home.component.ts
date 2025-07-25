import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  candidateId: string | null = localStorage.getItem('candidate_id');
  status = '';
  currentLevel: number | null = null;
  eliminatedLevel: number | null = null;
  totalScore: number | null = null;
  loading = false;
  message = '';
  incompleteRound = false;
  interviewProgress: any = {};
  maxMarksPerRound = 60;


  constructor(private api: ApiService, private router: Router) {}

  ngOnInit(): void {
    console.log('✅ Home component loaded');
    if (!this.candidateId) {
      this.router.navigate(['/register']);
      return;
    }

    this.api.getCandidateStatus().subscribe({
      next: (res: any) => {
        this.status = res.status;
        this.currentLevel = res.current_level;
        this.eliminatedLevel = res.eliminated_at_level;
        this.totalScore = res.total_score;
        this.incompleteRound = res.incomplete_round;
        this.interviewProgress = res.interview_progress || {};
      },
      error: () => {
        this.message = 'Error fetching candidate status.';
      }
    });

  }

  startInterview(): void {
    if (!this.candidateId) return;

    if (this.incompleteRound) {
      this.router.navigate(['/interview']);  // 👈 just resume
      return;
    }

    const round = this.currentLevel ? this.currentLevel + 1 : 1;
    const level = round;

    this.loading = true;
    this.api.startRound({ round, level }).subscribe({
      next: () => {
        this.router.navigate(['/interview']);
      },
      error: () => {
        this.message = 'Failed to start the interview round.';
        this.loading = false;
      }
    });
  }

  isCurrentLevelCompleted(): boolean {
    if (!this.currentLevel || !this.interviewProgress) return false;
    const progress = this.interviewProgress[this.currentLevel - 1];
    console.log(progress)
    console.log(progress?.completed === true)
    return progress?.completed === true;
  }

  isCurrentLevelPassed(): boolean {
    if (!this.currentLevel || !this.interviewProgress) return false;
    const progress = this.interviewProgress[this.currentLevel - 1];
    return progress?.completed === true && progress?.passed === true;
  }
}
