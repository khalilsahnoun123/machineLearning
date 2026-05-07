import { Component, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PredictionService } from '../../services/prediction';

@Component({
  selector: 'app-anomaly',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './anomaly.html',
  styleUrls: ['./anomaly.css']
})
export class AnomalyComponent {

  student = {
    age: 25,
    attendance_rate: 0.75,
    avg_test_score: 70,
    engagement_score: 0.6,
    login_frequency_per_week: 3,
    time_spent_hours_per_week: 6,
    days_since_last_login: 7,
    course_completion_rate: 0.65,
    assignment_submission_rate: 0.7,
    video_watch_percentage: 0.6,
    payment_delay_days: 0,
    discount_used: 0,
    upgrade_history: 0,
    churn_risk: 0.3,
    academic_success: 'Average'
  };

  result: any = null;
  loading = false;
  error = '';

  academicSuccesses = ['Low', 'Average', 'High'];

  constructor(
    private predictionService: PredictionService,
    private cdr: ChangeDetectorRef
  ) {}

  predict() {
    this.loading = true;
    this.result = null;
    this.error = '';
    this.cdr.detectChanges();

    this.predictionService.predictAnomaly(this.student).subscribe({
      next: (res) => {
        this.result = res;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Cannot connect to the anomaly API. Make sure Flask is running on port 5004.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  getResultColor(): string {
    if (!this.result) return '#6B7A99';
    return this.result.is_anomaly ? '#d94a38' : '#008f6f';
  }

  getScoreText(): string {
    if (!this.result || this.result.anomaly_score === null || this.result.anomaly_score === undefined) {
      return 'Model score unavailable';
    }
    return this.result.anomaly_score;
  }
}
