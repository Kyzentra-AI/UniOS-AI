export type RoadmapScope =
  | 'ACADEMIC'
  | 'CAREER'
  | 'BOTH';

export type RoadmapStatus =
  | 'ACTIVE'
  | 'INACTIVE';

export type RoadmapGenerationStatus =
  | 'PROCESSING'
  | 'ACTIVE';

export type MissionType =
  | 'LEARNING'
  | 'REVISION'
  | 'ASSIGNMENT'
  | 'PRACTICAL'
  | 'ARTIFACT'
  | 'CAREER';

export type MissionStatus =
  | 'PENDING'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'DEFERRED'
  | 'SKIPPED';

export interface RoadmapRequest {
  syllabus_id: string;
  scope: RoadmapScope;
}

export interface RoadmapGenerationResponse {
  message: string;
  status: 'PROCESSING';
}

export interface RoadmapMission {
  id: string;
  roadmap_id: string;
  title: string;
  description: string;
  mission_type: MissionType;
  subject?: string | null;
  priority: string;
  estimated_minutes: number;
  week: number;
  sequence: number;
  status: MissionStatus;
}

export interface RoadmapSubject {
  name: string;
  topics: string[];
}

export interface RoadmapSemester {
  name: string;
  subjects: RoadmapSubject[];
}

export interface RoadmapCareer {
  goals: string[];
}

export interface RoadmapScopeData {
  scope: string;
  semesters: RoadmapSemester[];
  career?: RoadmapCareer | null;
  goals: string[];
  milestones: string[];
  missions: RoadmapPlanMission[];
}

export interface RoadmapPlanMission {
  title: string;
  type: MissionType;
  description: string;
  priority: string;
  estimated_minutes: number;
  subject?: string | null;
  week: number;
  sequence: number;
}

export interface Roadmap {
  id: string;
  version: number;
  scope: RoadmapScope;
  status: RoadmapStatus;
  scope_data: RoadmapScopeData;
  missions: RoadmapMission[];
  created_at?: string | null;
  updated_at?: string | null;
}

export interface RoadmapResponse {
  roadmap: Roadmap | null;
}