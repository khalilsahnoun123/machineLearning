import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
 
@Injectable({
  providedIn: 'root'
})
export class PredictionService {
 
  private churnApiUrl        = 'http://127.0.0.1:5001/predict';
  private segmentationApiUrl = 'http://127.0.0.1:5000/predict';
  private packageApiUrl      = 'http://127.0.0.1:5003/predict';
 
  constructor(private http: HttpClient) {}
 
  predictChurn(data: any): Observable<any> {
    return this.http.post(this.churnApiUrl, data);
  }
 
  predictSegmentation(data: any): Observable<any> {
    return this.http.post(this.segmentationApiUrl, data);
  }
 
  predictPackage(data: any): Observable<any> {
    return this.http.post(this.packageApiUrl, data);
  }
}
 