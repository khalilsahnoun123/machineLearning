import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
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
export class SegmentationComponent implements OnInit {

  loading = false;

  formData: any = {
    attendance_rate:      75,
    avg_test_score:       70,
    engagement_score:     60,
    assignment_completion: 80,
    study_hours_weekly:   10,
  };

  result: any = null;

  // ── Radar geometry constants ──────────────────────────────────────────────
  readonly LABELS = [
    'Attendance', 'Test Score', 'Engagement', 'Assignments', 'Study Hrs',
  ];

  /** Background ring radii (percentages of max = 100) */
  rings = [20, 40, 60, 80, 100];

  /** Axis end-points on the SVG (center = 150,150, max radius = 110) */
  axes = this._buildAxes();

  constructor(
    private predictionService: PredictionService,
    private cd: ChangeDetectorRef,
  ) {}

  ngOnInit() {}

  onSlider() { /* triggers ngModel change detection */ }

  // ── API call ──────────────────────────────────────────────────────────────

  predict() {
  if (this.loading) return;   // ← prevent double-submit
  this.loading = true;
  this.result = null;

  this.predictionService.predictSegmentation(this.formData).subscribe({
    next: (res: any) => {
      this.result = res;
      this.loading = false;
      this.cd.markForCheck();      // ← swap detectChanges for markForCheck
    },
    error: (err) => {
      console.error(err);
      this.loading = false;
      this.cd.markForCheck();
    }
  });
}
  // ── CSS class helpers ─────────────────────────────────────────────────────

  riskClass(): string {
    const r = this.result?.risk ?? '';
    if (r.includes('Low'))         return 'risk-low';
    if (r.includes('High Risk'))   return 'risk-high';
    if (r.includes('Medium-High')) return 'risk-medium-high';
    return 'risk-medium';
  }

  barColor(value: number): string {
    if (value >= 75) return '#27AE60';
    if (value >= 50) return '#F39C12';
    return '#C0392B';
  }

  // ── Metric bars ───────────────────────────────────────────────────────────

  metricBars(): { label: string; value: number }[] {
    if (!this.result?.radar) return [];
    return Object.entries(this.result.radar).map(([label, value]) => ({
      label,
      value: Math.round(value as number),
    }));
  }

  // ── Radar chart helpers ───────────────────────────────────────────────────

  private _buildAxes() {
    const n = 5;
    const cx = 150, cy = 150, r = 110;
    return Array.from({ length: n }, (_, i) => {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      return { x2: cx + r * Math.cos(angle), y2: cy + r * Math.sin(angle) };
    });
  }

  /** Convert a ring radius (0-100) to a polygon points string */
  hexPoints(pct: number): string {
    const n = 5, cx = 150, cy = 150, maxR = 110;
    const r = (pct / 100) * maxR;
    return Array.from({ length: n }, (_, i) => {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      return `${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`;
    }).join(' ');
  }

  /** Data polygon points from radar scores */
  radarPoints(): string {
    return this.radarDots().map(p => `${p.x},${p.y}`).join(' ');
  }

  radarDots(): { x: number; y: number }[] {
    if (!this.result?.radar) return [];
    const values = Object.values(this.result.radar) as number[];
    const n = values.length, cx = 150, cy = 150, maxR = 110;
    return values.map((v, i) => {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const r = (Math.min(v, 100) / 100) * maxR;
      return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
    });
  }

  radarLabels(): { x: number; y: number; name: string; anchor: string }[] {
    if (!this.result?.radar) return [];
    const labels = Object.keys(this.result.radar);
    const n = labels.length, cx = 150, cy = 150, labelR = 128;
    return labels.map((name, i) => {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const x = cx + labelR * Math.cos(angle);
      const y = cy + labelR * Math.sin(angle);
      let anchor = 'middle';
      if (x < cx - 5) anchor = 'end';
      else if (x > cx + 5) anchor = 'start';
      return { x, y: y + 4, name, anchor };
    });
  }
}