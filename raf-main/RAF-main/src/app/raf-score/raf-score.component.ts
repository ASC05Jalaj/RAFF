import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { IcdCodeSearchService } from "../services/raf-score.service";
import { DiagnosisResult, PotentialCondition } from "../model/diagnosis-result.model";
import { debounceTime, switchMap, catchError, distinctUntilChanged, throttleTime } from 'rxjs/operators';
import { of } from 'rxjs';


interface AcceptedPotentialCondition {
  hccCode: string;
  rafScore: number;
}

@Component({
  selector: 'app-raf-score',
  templateUrl: './raf-score.component.html',
  styleUrls: ['./raf-score.component.css'],
})
export class RafScoreComponent implements OnInit {
  riskScoreForm: FormGroup;
  results: DiagnosisResult[] = [];
  demographicRiskFactor: number = 0;
  addedDiagnosisCodes: string[] = [];
  hoveredCode: string | null = null;
  icdSuggestions: { code: string, description: string }[] = [];
  selectedDiagnosisDescription: string = '';
  loading: boolean = false;
  errorFetchingSuggestions: boolean = false;
  private icdCache = new Map<string, { code: string, description: string }[]>();
  private typingTimeout: any;
  potentialConditions: PotentialCondition[] = [];
  acceptedPotentialConditions: AcceptedPotentialCondition[] = [];
  isSubmitted: boolean = false;
  

  constructor(private fb: FormBuilder, private icdService: IcdCodeSearchService) {
    this.riskScoreForm = this.fb.group({
      gender: ['', Validators.required],
      diagnosis_code: [''],
      age: ['', [Validators.required, Validators.min(0)]],
      eligibility: ['', Validators.required],
      model_name: ['', Validators.required],
    });
  }

  ngOnInit(): void {
    this.setupDiagnosisCodeAutoComplete();
    
  }

  

  private setupDiagnosisCodeAutoComplete() {
    this.riskScoreForm.get('diagnosis_code')?.valueChanges.pipe(
      debounceTime(500),
      throttleTime(1000),
      distinctUntilChanged(),
      switchMap((query: string) => {
        if (query) {
          if (this.icdCache.has(query)) {
            this.icdSuggestions = this.icdCache.get(query)!;
            return of([]);
          } else {
            this.loading = true;
            this.errorFetchingSuggestions = false;
            return this.icdService.searchIcdCodeSuggestions(query).pipe(
              catchError((error) => {
                console.error('Error fetching ICD-10 suggestions', error);
                this.errorFetchingSuggestions = true;
                this.loading = false;
                return of([]);
              })
            );
          }
        }
        this.icdSuggestions = [];
        return of([]);
      })
    ).subscribe((suggestions) => {
      if (suggestions.length > 0) {
        this.icdCache.set(this.riskScoreForm.get('diagnosis_code')?.value, suggestions);
      }
      this.loading = false;
      this.icdSuggestions = suggestions;
    });
  }

  onDiagnosisCodeInputChange() {
    const diagnosisCode = this.riskScoreForm.get('diagnosis_code')?.value;
    if (diagnosisCode) {
      if (this.typingTimeout) {
        clearTimeout(this.typingTimeout);
      }
      this.typingTimeout = setTimeout(() => {
        this.fetchSuggestions(diagnosisCode);
      }, 500);
    } else {
      this.icdSuggestions = [];
    }
  }

  fetchSuggestions(query: string) {
    this.loading = true;
    this.errorFetchingSuggestions = false;
    if (this.icdCache.has(query)) {
      this.icdSuggestions = this.icdCache.get(query)!;
      this.loading = false;
    } else {
      this.icdService.searchIcdCodeSuggestions(query).subscribe(
        (response) => {
          this.icdSuggestions = response.map(item => ({
            code: item.code,
            description: item.description,
          }));
          this.icdCache.set(query, this.icdSuggestions);
          this.loading = false;
        },
        (error) => {
          console.error('Error fetching ICD-10 suggestions', error);
          this.errorFetchingSuggestions = true;
          this.loading = false;
        }
      );
    }
  }

  selectIcdCode(suggestedCode: string, description: string) {
    if (!this.addedDiagnosisCodes.includes(suggestedCode)) {
      this.addedDiagnosisCodes.push(suggestedCode);
      this.selectedDiagnosisDescription = description;
    }
    this.clearDiagnosisCodeField();
    this.icdSuggestions = [];
  }

  onSubmit() {
    if (this.addedDiagnosisCodes.length === 0) {
      alert('Please add at least one diagnosis code.');
      return;
    }

    if (this.riskScoreForm.valid) {
      const data = {
        diagnosis_code: this.addedDiagnosisCodes.join(','),
        gender: this.riskScoreForm.get('gender')?.value,
        age: this.riskScoreForm.get('age')?.value,
        eligibility: this.riskScoreForm.get('eligibility')?.value,
        model_name: this.riskScoreForm.get('model_name')?.value,
      };

      this.icdService.searchDiagnosisCode(data).subscribe(
        (response: any) => {
          this.results = response.results;
          this.potentialConditions = response.potentialConditions;
          this.isSubmitted = true;
          this.getDemographicRiskFactor();
        },
        (error) => {
          alert('Please enter valid details');
        }
      );
    } else {
      alert('Please fill all required fields');
    }
  }

  removeDiagnosisCode(index: number) {
    this.addedDiagnosisCodes.splice(index, 1);
    if (this.isSubmitted && this.addedDiagnosisCodes.length > 0) {
      this.onSubmit();
    }
  }

  getDemographicRiskFactor() {
    const data = {
      age: this.riskScoreForm.get('age')?.value,
      gender: this.riskScoreForm.get('gender')?.value,
      eligibility: this.riskScoreForm.get('eligibility')?.value,
      model_name: this.riskScoreForm.get('model_name')?.value
    };

    this.icdService.getDemographicRiskFactor(data).subscribe(
      (response) => {
        this.demographicRiskFactor = response.demographicRiskFactor;
      },
      (error) => {
        alert('Failed to fetch demographic risk factor');
      }
    );
  }

  getTotalPotentialRafScore(): number {
    return this.acceptedPotentialConditions.reduce((sum, condition) => sum + condition.rafScore, 0);
  }

  getTotalRafScore(): number {
    const actualScore = this.results.reduce((sum, result) => sum + (result.Risk_Score || 0), 0);
    return actualScore;
  }

  getFinalTotalScore(): number {
    return this.getTotalRafScore() + this.getTotalPotentialRafScore() + this.demographicRiskFactor;
  }

  clearAcceptedPotentialConditions() {
    this.acceptedPotentialConditions = [];
  }

  clearDiagnosisCodeField() {
    const diagnosisControl = this.riskScoreForm.get('diagnosis_code');
    if (diagnosisControl) {
      diagnosisControl.setValue('');
      diagnosisControl.markAsPristine();
      diagnosisControl.markAsUntouched();
    }
  }

  onReset() {
    this.addedDiagnosisCodes = [];
    this.results = [];
    this.potentialConditions = [];
    this.acceptedPotentialConditions = [];
    this.isSubmitted = false;
    this.riskScoreForm.reset();
  }

  getRafScore(code: string): number {
    const result = this.results.find(r => r.DIAG === code);
    return result ? result.Risk_Score : 0;
  }

  getDiagnosisDescription(code: string): string {
    const result = this.results.find(r => r.DIAG === code);
    return result ? result.ICD_Description : "N/A";
  }

  onPotentialConditionAccept(condition: PotentialCondition) {
    // Add to accepted potential conditions
    this.acceptedPotentialConditions.push({
      hccCode: condition.hccCode,
      rafScore: condition.rafScore
    });

    // Remove from potential conditions table
    this.potentialConditions = this.potentialConditions.filter(
      pc => pc.diagnosisCode !== condition.diagnosisCode
    );
  }

  onPotentialConditionReject(condition: PotentialCondition) {
    this.potentialConditions = this.potentialConditions.filter(
      pc => pc.diagnosisCode !== condition.diagnosisCode
    );
  }

  onMouseEnter(code: string) {
    this.hoveredCode = code;
  }

  onMouseLeave() {
    this.hoveredCode = null;
  }
  

}
