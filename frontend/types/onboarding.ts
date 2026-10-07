export type AcademicStatus =
  | 'BACHELOR'
  | 'MASTER'
  | 'RECENT_GRADUATE';

export type DailyStudyHours =
  | 'LESS_THAN_1'
  | '1_2'
  | '2_3'
  | '3_4'
  | '4_PLUS';

export type LearningDepth =
  | 'QUICK'
  | 'BALANCED'
  | 'DEEP';

export interface LearnerProfilePayload {
  primary_goal?: string;
  target_skills?: string[];
  skills?: string[];
  projects?: string[];
  research?: string | null;
  experience?: string | null;
}

export interface AcademicProfilePayload {
  academic_status?: AcademicStatus;
  university?: string | null;
  degree_program?: string;
  domain?: string;
  current_year?: string | null;
  graduation_year?: number | null;
  subjects?: string[];
}

export interface LearningPreferencesPayload {
  daily_study_hours?: DailyStudyHours;
  learning_depth?: LearningDepth;
}

export interface OnboardingPayload {
  learner_profile?: LearnerProfilePayload;
  academic_profile?: AcademicProfilePayload;
  learning_preferences?: LearningPreferencesPayload;
}

export type OnboardingPatchPayload = OnboardingPayload;

export interface OnboardingRawData {
  learner_profile: {
    id: string;
    user_id: string;
    primary_goal: string;
    target_skills: string[];
    skills: string[];
    projects: string[];
    research: string | null;
    experience: string | null;
    onboarding_status: 'IN_PROGRESS' | 'COMPLETED';
    onboarding_version: number;
  };

  academic_profile: {
    academic_status: AcademicStatus;
    university: string | null;
    degree_program: string;
    domain: string;
    current_year: string | null;
    graduation_year: number | null;
    subjects: string[];
  };

  learning_preferences: {
    daily_study_hours: DailyStudyHours;
    learning_depth: LearningDepth;
  };
}

export interface OnboardingState {
  status: 'IN_PROGRESS' | 'COMPLETED';
  raw_data: OnboardingRawData;
  context: Record<string, unknown>;
}

export interface CompleteOnboardingResponse {
  message: string;
}


export interface KIEQuestion {
  question_id: string;
  text: string;
  type: string;
  options: string[];
}

export interface KIEQuestionsProcessingResponse {
  status: 'processing';
  message: string;
}

export interface KIEQuestionsSuccessResponse {
  status: 'success';
  message: string;
}

export interface KIEQuestionsReadyResponse {
  status: 'pending_context';
  questions: KIEQuestion[];
}

export type KIEQuestionsResponse =
  | KIEQuestionsProcessingResponse
  | KIEQuestionsSuccessResponse
  | KIEQuestionsReadyResponse;

export interface OnboardingAnswer {
  question_id: string;
  answer: unknown;
}

export interface OnboardingAnswersPayload {
  answers: OnboardingAnswer[];
}

export interface OnboardingAnswersResponse {
  status: 'processing';
  message: string;
}