import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DiagnosisResult } from '../model/diagnosis-result.model';
 
@Injectable({
  providedIn: 'root',
})
export class IcdCodeSearchService {
  private apiUrl = 'http://127.0.0.1:5000/api/risk-score';
  private icdSuggestionsUrl = 'http://127.0.0.1:5000/api/icd-suggestions';  // Corrected URL
 
  constructor(private http: HttpClient) {}
 
  searchDiagnosisCode(data: { diagnosis_code: string, gender: string, age: number, eligibility: string }): Observable<DiagnosisResult[]> {
    return this.http.post<DiagnosisResult[]>(this.apiUrl, data);
  }
 
  searchIcdCodeSuggestions(query: string): Observable<{ code: string; description: string }[]> {
    // Using the full URL for the icd-suggestions endpoint
    return this.http.get<{ code: string; description: string }[]>(`${this.icdSuggestionsUrl}?query=${query}`);
  }
 
  getDemographicRiskFactor(data: { age: number, gender: string, eligibility: string }): Observable<{ demographicRiskFactor: number }> {
    return this.http.post<{ demographicRiskFactor: number }>('http://127.0.0.1:5000/api/demographic-risk-score', data);
  }
}