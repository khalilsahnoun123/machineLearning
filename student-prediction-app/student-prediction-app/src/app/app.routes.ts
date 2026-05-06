import { Routes } from '@angular/router';
import { ChurnComponent } from './models/churn/churn';
import { SegmentationComponent } from './segmentation/segmentation';
import { PackageComponent } from './models/package/package';

export const routes: Routes = [
  { path: '', redirectTo: 'churn', pathMatch: 'full' },
  { path: 'churn', component: ChurnComponent },
  { path: 'segmentation', component: SegmentationComponent },
  { path: 'package', component: PackageComponent },
];