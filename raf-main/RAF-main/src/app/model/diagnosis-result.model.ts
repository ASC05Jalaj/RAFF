export interface DiagnosisResult {
  DIAG: string;
  SEX: string;
  Age: number;
  // Description: string;
  Eligibility: string;
  Risk_Score: number;
  HCC_Code: string;
  HCC_Description: string; // Existing field
  ICD_Description: string; // New field for ICD Description
}


export interface PotentialCondition {
  diagnosisCode: string;
  hccCode: string;
  rafScore: number;
  probability: number;
  description: string;
}