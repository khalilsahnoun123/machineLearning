import { ChangeDetectorRef, Component } from '@angular/core';
import { PredictionService } from '../services/prediction';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-segmentation',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './segmentation.html',
  styleUrl: './segmentation.css',
})
export class SegmentationComponent {

 
  loading = false;

  formData: any = {
    attendance_rate: 75,
    avg_test_score: 70,
    engagement_score: 60,
    assignment_completion: 80,
    study_hours_weekly: 10
  };

  result: any;

  constructor(
    private predictionService: PredictionService,
    private cd: ChangeDetectorRef
  ) {}

  predict() {

    this.loading = true;

    this.predictionService.predictSegmentation(this.formData)
      .subscribe({
        next: (res: any) => {

          this.result = res;

          this.loading = false;

          this.cd.detectChanges();
        },

        error: (err) => {
          console.error(err);
          this.loading = false;
        }
      });
  }
}