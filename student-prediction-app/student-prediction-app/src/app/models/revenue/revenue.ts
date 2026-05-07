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
  // Form data
  formData = {
    age: 20,
    gender: 'M',
    enrollment_year: 2023,
    program: 'Computer Science',
    gpa: 3.5,
    attendance_rate: 85,
    study_hours_per_week: 15,
    extracurricular_activities: 2,
    previous_education_level: 'High School',
    family_income: 50000,
    distance_from_home: 10,
    part_time_job: 0,
    scholarship: 1,
    health_status: 'Good',
    relationship_status: 'Single',
    stress_level: 3,
    social_support: 4,
    career_goals_clarity: 4,
    financial_stress: 2,
    academic_pressure: 3
  };

  // Prediction result
  prediction: number | null = null;
  loading = false;
  error: string | null = null;

  constructor(private predictionService: PredictionService) {}

  onSubmit() {
    this.loading = true;
    this.error = null;
    this.prediction = null;

    this.predictionService.predictRevenue(this.formData).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.status === 'success') {
          this.prediction = response.prediction;
        } else {
          this.error = 'Erreur lors de la prédiction';
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.error || 'Erreur de connexion à l\'API';
        console.error('Prediction error:', err);
      }
    });
  }

  resetForm() {
    this.formData = {
      age: 20,
      gender: 'M',
      enrollment_year: 2023,
      program: 'Computer Science',
      gpa: 3.5,
      attendance_rate: 85,
      study_hours_per_week: 15,
      extracurricular_activities: 2,
      previous_education_level: 'High School',
      family_income: 50000,
      distance_from_home: 10,
      part_time_job: 0,
      scholarship: 1,
      health_status: 'Good',
      relationship_status: 'Single',
      stress_level: 3,
      social_support: 4,
      career_goals_clarity: 4,
      financial_stress: 2,
      academic_pressure: 3
    };
    this.prediction = null;
    this.error = null;
  }

  getRevenueCategory(value: number): string {
    if (value < 1000) return 'Faible';
    if (value < 3000) return 'Moyen';
    if (value < 5000) return 'Élevé';
    return 'Très Élevé';
  }

  getRevenueColor(value: number): string {
    if (value < 1000) return '#ef4444';
    if (value < 3000) return '#f59e0b';
    if (value < 5000) return '#10b981';
    return '#3b82f6';
  }
}
