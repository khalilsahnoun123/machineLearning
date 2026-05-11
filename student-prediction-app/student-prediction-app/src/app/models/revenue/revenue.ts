import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PredictionService } from '../../services/prediction';

@Component({
  selector: 'app-revenue',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './revenue.html',
  styleUrl: './revenue.css'
})
export class RevenueComponent {
  // Form data - Based on actual dataset columns
  formData = {
    age: 28,
    gender: 'Male',
    english_level: 'Intermediate',
    attendance_rate: 92,
    avg_test_score: 78,
    engagement_score: 0.85,
    login_frequency_per_week: 8,
    time_spent_hours_per_week: 18,
    package_type: 'Standard',
    package_price: 150,
    package_duration_months: 6,
    total_payments: 900,
    churn_risk: 0.25,
    academic_success: 1,
    profession: 'Engineer',
    income_level: 'Medium',
    city: 'Tunis',
    registration_channel: 'Facebook',
    days_since_last_login: 1,
    course_completion_rate: 0.88,
    assignment_submission_rate: 0.92,
    video_watch_percentage: 0.95,
    discount_used: 0,
    payment_delay_days: 0,
    upgrade_history: 2,
    churn: 0
  };

  // Prediction result
  prediction: number | null = null;
  category: string | null = null;
  interpretation: string | null = null;
  executionTime: number | null = null;
  loading = false;
  error: string | null = null;

  constructor(private predictionService: PredictionService) {}

  onSubmit() {
    this.loading = true;
    this.error = null;
    this.prediction = null;
    this.category = null;
    this.interpretation = null;
    this.executionTime = null;

    const startTime = performance.now();

    this.predictionService.predictRevenue(this.formData).subscribe({
      next: (response) => {
        const endTime = performance.now();
        const totalTime = endTime - startTime;
        
        this.loading = false;
        if (response.status === 'success') {
          this.prediction = response.prediction;
          this.category = response.category || this.getRevenueCategory(response.prediction);
          this.interpretation = response.interpretation || '';
          this.executionTime = response.execution_time_ms || totalTime;
          
          console.log(`✓ Prediction completed in ${this.executionTime.toFixed(2)}ms`);
        } else {
          this.error = 'Error during prediction';
        }
      },
      error: (err) => {
        const endTime = performance.now();
        const totalTime = endTime - startTime;
        
        this.loading = false;
        this.error = err.error?.error || 'API connection error';
        console.error(`✗ Prediction failed after ${totalTime.toFixed(2)}ms:`, err);
      }
    });
  }

  resetForm() {
    this.formData = {
      age: 28,
      gender: 'Male',
      english_level: 'Intermediate',
      attendance_rate: 92,
      avg_test_score: 78,
      engagement_score: 0.85,
      login_frequency_per_week: 8,
      time_spent_hours_per_week: 18,
      package_type: 'Standard',
      package_price: 150,
      package_duration_months: 6,
      total_payments: 900,
      churn_risk: 0.25,
      academic_success: 1,
      profession: 'Engineer',
      income_level: 'Medium',
      city: 'Tunis',
      registration_channel: 'Facebook',
      days_since_last_login: 1,
      course_completion_rate: 0.88,
      assignment_submission_rate: 0.92,
      video_watch_percentage: 0.95,
      discount_used: 0,
      payment_delay_days: 0,
      upgrade_history: 2,
      churn: 0
    };
    this.prediction = null;
    this.category = null;
    this.interpretation = null;
    this.executionTime = null;
    this.error = null;
  }

  getRevenueCategory(value: number): string {
    if (value < 1000) return 'Low';
    if (value < 3000) return 'Average';
    if (value < 5000) return 'High';
    return 'Very High';
  }

  getRevenueColor(value: number): string {
    if (value < 1000) return '#ef4444';
    if (value < 3000) return '#f59e0b';
    if (value < 5000) return '#10b981';
    return '#3b82f6';
  }
}
