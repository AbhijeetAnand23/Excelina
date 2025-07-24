import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { ToastService } from '../../services/toast.service';

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

  loading: boolean = false;

  constructor(private api: ApiService, private router: Router, private toast: ToastService) {}

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
        this.toast.show('error', 'Failed to load questions. Please try again.');
      }
    });
  }


  submitAnswer(): void {
    if (!this.userAnswer.trim()) {
      this.toast.show('error', 'Please enter your answer before submitting.');
      return;
    }

    this.loading = true;

    const question = this.questions[this.currentIndex];

    this.api.submitAnswer({
      candidate_id: this.candidateId,
      question_id: question.question_id,
      user_answer: this.userAnswer
    }).subscribe({
      next: () => {
        this.toast.show('success', 'Answer submitted!');

        this.userAnswer = '';
        this.currentIndex++;
        this.loading = false;

        if (this.currentIndex === this.questions.length) {
          // Final question: Complete the round
          this.loading = true;
          this.api.completeRound().subscribe({
            next: (res: any) => {
              this.loading = false;
              this.router.navigate(['/feedback']);
            },
            error: () => {
              this.loading = false;
              this.toast.show('error', 'Something went wrong. Please try again after a few seconds.');
            }
          });
        }
      },
      error: () => {
        this.loading = false;
        this.toast.show('error', 'Something went wrong. Please try again after a few seconds.');
      }
    });
  }
}
