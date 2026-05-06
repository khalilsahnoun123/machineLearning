import { Routes } from '@angular/router';
import { ChurnComponent } from './models/churn/churn';
import { SegmentationComponent } from './segmentation/segmentation';

export const routes: Routes = [
{ path: '', redirectTo: 'segmentation', pathMatch: 'full' },
  { path: 'churn', component: ChurnComponent },
    { path: 'segmentation', component: SegmentationComponent },

];