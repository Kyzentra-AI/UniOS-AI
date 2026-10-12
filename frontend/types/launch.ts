export type LaunchTab = 'overview' | 'resume' | 'ats';

export interface ResumeEducation {
  id: string;
  institution: string;
  degree: string;
  startYear: string;
  endYear: string;
  grade: string;
}

export interface ResumeProject {
  id: string;
  name: string;
  description: string;
  technologies: string;
  link: string;
}

export interface ResumeAchievement {
  id: string;
  title: string;
  description: string;
}

export interface ResumeDraft {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  headline: string;
  summary: string;
  skills: string;
  education: ResumeEducation[];
  projects: ResumeProject[];
  achievements: ResumeAchievement[];
}

export interface ATSFinding {
  id: string;
  category: 'structure' | 'content' | 'formatting';
  severity: 'info' | 'warning' | 'critical';
  title: string;
  description: string;
  suggestion: string;
}

export interface ATSAnalysisResult {
  findings: ATSFinding[];
  score?: number;
  summary?: string;
}