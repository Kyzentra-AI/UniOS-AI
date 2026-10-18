export type MentorMode =
  | 'tutor'
  | 'study-coach'
  | 'accountability'
  | 'motivation';

export interface MentorContext {
  learnerId?: string;
  roadmapId?: string;
  missionId?: string;
  lessonId?: string;
  topic?: string;
}

export interface MentorMessage {
  id: string;
  role: 'user' | 'mentor';
  content: string;
  createdAt?: string;
}

export interface MentorConversation {
  id: string;
  mode: MentorMode;
  messages: MentorMessage[];
}