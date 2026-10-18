export type LessonBlockType =
  | 'TEXT'
  | 'VIDEO'
  | 'INTERACTIVE'
  | 'QUIZ'
  | 'CODE';

export interface LessonBlock {
  id: string;
  type: LessonBlockType | string;
  title?: string | null;
  content?: string | null;
  code?: string | null;
  language?: string | null;
  options?: string[] | null;
  answer?: string | null;
  explanation?: string | null;
  url?: string | null;
  caption?: string | null;
}

export interface Lesson {
  id: string;
  title: string;
  objective: string;
  prerequisites?: string[] | null;
  blocks: LessonBlock[];
}

export type LearningSessionStatus =
  | 'IN_PROGRESS'
  | 'PAUSED'
  | 'COMPLETED';

export interface LearningSessionCreate {
  roadmap_id?: string;
  mission_id?: string;
  topic: string;
  lesson_id: string;
}

export interface LearningSessionUpdate {
  status?: LearningSessionStatus;
  checkpoint_block_id?: string;
  progress_percentage?: number;
  notes?: string;
}

export interface LearningSession {
  id: string;
  learner_id: string;
  roadmap_id?: string | null;
  mission_id?: string | null;
  topic: string;
  lesson_id: string;
  status: LearningSessionStatus | string;
  checkpoint_block_id?: string | null;
  progress_percentage: number;
  lesson_data?: Record<string, unknown> | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContentReference {
  [key: string]: unknown;
}

export interface ContentReferenceResponse {
  topic: string;
  references: ContentReference[];
}
