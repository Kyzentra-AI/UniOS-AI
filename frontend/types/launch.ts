
export type ISODateTime = string;

export type ResumeSource = 'profile' | 'manual';
export type ResumeStatus = 'draft' | 'generated';

export interface ResumeContact {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  linkedInUrl: string;
  githubUrl: string;
  portfolioUrl: string;
}

export interface ResumeEducation {
  id: string;
  institution: string;
  degree: string;
  fieldOfStudy: string;
  startDate: string;
  endDate: string;
  grade: string;
}

export interface ResumeExperience {
  id: string;
  company: string;
  role: string;
  location: string;
  startDate: string;
  endDate: string;
  isCurrent: boolean;
  description: string;
}

export interface ResumeProject {
  id: string;
  name: string;
  description: string;
  technologies: string[];
  projectUrl: string;
  startDate: string;
  endDate: string;
}

export interface ResumeAchievement {
  id: string;
  title: string;
  description: string;
  date: string;
}

export interface ResumeDraft {
  contact: ResumeContact;
  headline: string;
  summary: string;
  skills: string[];
  education: ResumeEducation[];
  experience: ResumeExperience[];
  projects: ResumeProject[];
  achievements: ResumeAchievement[];
}

export interface ResumePreferences {
  targetRole?: string;
  tone?: 'professional' | 'concise';
}

export interface ResumeRecord {
  id: string;
  title: string;
  source: ResumeSource;
  status: ResumeStatus;
  content: ResumeDraft;
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
}

export interface ProfileResumePreviewResponse {
  content: ResumeDraft;
  missingFields: string[];
}

export interface CreateResumeRequest {
  title: string;
  source: ResumeSource;
  content: ResumeDraft;
}

export interface UpdateResumeRequest {
  title: string;
  content: ResumeDraft;
}

export interface GenerateResumeRequest extends CreateResumeRequest {
  preferences?: ResumePreferences;
}

export interface GenerateResumeResponse {
  resume: ResumeRecord;
  provider: 'llm' | 'template' | 'hybrid';
}

export interface ResumeListResponse {
  items: ResumeRecord[];
}

export interface ResumeDetailResponse {
  resume: ResumeRecord;
}

export type ATSFindingCategory =
  | 'structure'
  | 'content'
  | 'formatting'
  | 'contact_information'
  | 'missing_information'
  | 'readability';

export type ATSFindingSeverity = 'info' | 'warning' | 'critical';

export interface ATSFinding {
  id: string;
  category: ATSFindingCategory;
  severity: ATSFindingSeverity;
  title: string;
  description: string;
  recommendation: string;
}

export interface ATSScore {
  value: number;
  maxValue: number;
  methodology: string;
  methodologyVersion: string;
}

export interface ATSDocumentMetadata {
  fileName: string;
  fileType: 'pdf' | 'docx';
  pageCount: number | null;
  extractedCharacterCount: number;
}

export interface ATSAnalysisRecord {
  id: string;
  status: 'completed' | 'failed';
  document: ATSDocumentMetadata;
  score: ATSScore | null;
  summary: string;
  findings: ATSFinding[];
  createdAt: ISODateTime;
}

export interface ATSAnalysisResponse {
  analysis: ATSAnalysisRecord;
}

export interface ATSAnalysisHistoryResponse {
  items: ATSAnalysisRecord[];
}

export interface APIError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  requestId?: string;
}
