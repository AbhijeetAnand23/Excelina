import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-interview',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './interview.component.html',
  styleUrls: ['./interview.component.scss']
})
export class InterviewComponent implements OnInit {
  candidateId: string | null = '';
  questions: any[] = [];
  currentIndex = 0;
  userAnswer = '';

  errorMessage = '';
  successMessage = '';

  constructor(private api: ApiService, private router: Router) {}

  get totalQuestions(): number {
    return this.questions.length;
  }

  get currentQuestion(): any {
    return this.questions[this.currentIndex];
  }

  ngOnInit(): void {
    this.candidateId = localStorage.getItem('candidate_id');
    if (!this.candidateId) {
      this.router.navigate(['/register']);
      return;
    }

    this.api.getQuestions(this.candidateId).subscribe({
      next: (res: any) => {
        this.questions = res;

        const firstUnansweredIndex = this.questions.findIndex(q => q.score === null);
        this.currentIndex = firstUnansweredIndex !== -1 ? firstUnansweredIndex : 0;

        // Preload answer if it's a previously answered one
        this.userAnswer = this.questions[this.currentIndex]?.user_answer || '';
      },
      error: () => {
        this.errorMessage = 'Failed to load questions. Please try again.';
      }
    });
  }


  submitAnswer(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.userAnswer.trim()) {
      this.errorMessage = 'Please enter your answer before submitting.';
      return;
    }

    const question = this.questions[this.currentIndex];

    this.api.submitAnswer({
      candidate_id: this.candidateId,
      question_id: question.question_id,
      user_answer: this.userAnswer
    }).subscribe({
      next: () => {
        this.successMessage = 'Answer submitted successfully!';
        this.userAnswer = '';
        this.currentIndex++;

        if (this.currentIndex === this.questions.length) {
          // 🟡 Evaluate the round
          this.api.completeRound().subscribe({
            next: (res: any) => {
              // if (res.status === 'eliminated' || res.status === 'completed') {
              //   this.router.navigate(['/feedback']);
              // } else {
              //   this.router.navigate(['/home']);
              // }
              this.router.navigate(['/feedback']);
            },
            error: () => {
              this.errorMessage = 'Error evaluating round. Please try again.';
            }
          });
        }
      },
      error: () => {
        this.errorMessage = 'Something went wrong while submitting your answer.';
      }
    });
  }
}
