import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { PredictionService } from '../../services/prediction';

@Component({
  selector: 'app-churn',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './churn.html',
styleUrls: ['./churn.css']
})
export class ChurnComponent {

  student = {
    age: 25,
    course_completion_rate: 0.5,
    attendance_rate: 0.7,
    avg_test_score: 60,
    days_since_last_login: 10,
    english_level: 'Intermediate',
    upgrade_history: 0,
    package_duration_months: 6,
    total_payments: 5,
    registration_channel: 'Facebook',
    profession: 'Student'
  };

  result: any = null;
  loading     = false;
  error       = '';

  englishLevels = ['Beginner', 'Intermediate', 'Advanced'];
  channels      = ['Facebook', 'Instagram', 'Google Ads', 'Referral'];
  professions   = ['Student', 'Teacher', 'Engineer', 'Doctor', 'Freelancer', 'Employee'];

  constructor(private predictionService: PredictionService) {}

  predict() {
    this.loading = true;
    this.result  = null;
    this.error   = '';

    this.predictionService.predictChurn(this.student).subscribe({
      next: (res) => {
        this.result  = res;
        this.loading = false;
      },
      error: () => {
        this.error   = 'Cannot connect to the prediction API. Make sure Flask is running on port 5001.';
        this.loading = false;
      }
    });
  }

  getRiskColor(): string {
    if (!this.result) return '#ccc';
    if (this.result.risk_level === 'High')   return '#e74c3c';
    if (this.result.risk_level === 'Medium') return '#f39c12';
    return '#27ae60';
  }

  getProgressWidth(): string {
    if (!this.result) return '0%';
    return this.result.probability_percent + '%';
  }
}