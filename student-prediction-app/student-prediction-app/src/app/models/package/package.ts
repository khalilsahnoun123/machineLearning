import { Component, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PredictionService } from '../../services/prediction';

@Component({
  selector: 'app-package',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './package.html',
  styleUrls: ['./package.css']
})
export class PackageComponent {

  student = {
    age: 25,
    gender: 'Male',
    english_level: 'Intermediate',
    attendance_rate: 0.7,
    avg_test_score: 60,
    engagement_score: 0.6,
    login_frequency_per_week: 3,
    time_spent_hours_per_week: 5,
    churn_risk: 0.3,
    academic_success: 'Average',
    profession: 'Student',
    income_level: 'Medium',
    city: 'Tunis',
    registration_channel: 'Online',
    days_since_last_login: 5,
    course_completion_rate: 0.6,
    assignment_submission_rate: 0.7,
    video_watch_percentage: 0.5,
    discount_used: 0,
    payment_delay_days: 0,
    upgrade_history: 0,
    churn: 0
  };

  result: any = null;
  loading = false;
  error = '';

  englishLevels     = ['Beginner', 'Intermediate', 'Advanced'];
  genders           = ['Male', 'Female'];
  academicSuccesses = ['Low', 'Average', 'High'];
  professions       = ['Student', 'Teacher', 'Engineer', 'Doctor', 'Freelancer', 'Employee'];
  incomeLevels      = ['Low', 'Medium', 'High'];
  channels          = ['Online', 'Facebook', 'Instagram', 'Google Ads', 'Referral'];
  cities            = ['Tunis', 'Sfax', 'Sousse', 'Bizerte', 'Nabeul', 'Other'];

  constructor(
    private predictionService: PredictionService,
    private cdr: ChangeDetectorRef
  ) {}

  predict() {
    this.loading = true;
    this.result  = null;
    this.error   = '';
    this.cdr.detectChanges();

    this.predictionService.predictPackage(this.student).subscribe({
      next: (res) => {
        console.log('Result reçu:', res);
        this.result  = res;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.log('Erreur:', err);
        this.error   = 'Cannot connect to the prediction API. Make sure Flask is running on port 5003.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  getPackageColor(): string {
    if (!this.result) return '#ccc';
    if (this.result.prediction === 'Premium')  return '#8e44ad';
    if (this.result.prediction === 'Standard') return '#2980b9';
    return '#27ae60';
  }

  getPackageIcon(): string {
    if (!this.result) return '';
    if (this.result.prediction === 'Premium')  return '👑';
    if (this.result.prediction === 'Standard') return '⭐';
    return '📦';
  }
}