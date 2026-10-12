export type AssessmentType =
  | 'mcq'
  | 'subjective'
  | 'viva'
  | 'case-study'
  | 'coding';

export interface AssessmentOption {
  id: string;
  text: string;
}

export interface AssessmentQuestion {
  id: string;
  type: AssessmentType;
  question: string;
  options?: AssessmentOption[];
  code?: string;
  language?: string;
}

export interface Assessment {
  id: string;
  title: string;
  type: AssessmentType;
  instructions?: string;
  questions: AssessmentQuestion[];
}

export type AssessmentAnswerValue =
  | string
  | string[]
  | Record<string, unknown>;

export interface BackendAssessmentAnswer {
  question_id: string;
  answer: AssessmentAnswerValue;
  hints_used: number;
  time_spent_seconds: number;
}

export interface AssessmentAttemptCreate {
  session_id?: string;
  assessment_id: string;
  topic: string;
  answers: BackendAssessmentAnswer[];
  total_time_spent_seconds: number;
  is_completed: boolean;
}

export interface AssessmentAttemptResponse {
  id: string;
  session_id?: string | null;
  learner_id: string;
  assessment_id: string;
  topic: string;
  answers: BackendAssessmentAnswer[];
  score?: number | null;
  total_time_spent_seconds: number;
  hints_used_count: number;
  is_completed: boolean;
  mastery_updates?: Record<string, unknown> | null;
  feedback?: string | null;
  created_at: string;
}
