
export type RoadmapScope = "ACADEMIC" | "CAREER" | "BOTH";

export type RoadmapStatus = "ACTIVE" | "INACTIVE";

export type RoadmapGenerationStatus = "PROCESSING" | "ACTIVE";

export type MissionType =
  | "LEARNING"
  | "REVISION"
  | "ASSIGNMENT"
  | "PRACTICAL"
  | "ARTIFACT"
  | "CAREER";

export type MissionStatus =
  | "PENDING"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "DEFERRED"
  | "SKIPPED";

export interface RoadmapRequest {
  syllabus_id: string;
  scope: RoadmapScope;
  subject?: string;
}

export interface RoadmapGenerationResponse {
  message: string;
  status: "PROCESSING";
  subject?: string | null;
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

export interface RoadmapSubjectTrack {
  subject_name: string;
  mission_count: number;
  estimated_total_minutes: number;
  core_topics: string[];
}

export interface RoadmapScopeData {
  scope?: string;
  target_subject?: string | null;
  subject_tracks?: RoadmapSubjectTrack[];
  semesters?: RoadmapSemester[];
  career?: RoadmapCareer | null;
  goals?: string[];
  milestones?: string[];
  missions?: RoadmapPlanMission[];
}

export interface Roadmap {
  id: string;
  version: number;
  scope: RoadmapScope;
  subject?: string | null;
  status: RoadmapStatus;
  scope_data: RoadmapScopeData;
  missions: RoadmapMission[];
  created_at?: string | null;
  updated_at?: string | null;
}

export interface RoadmapSubjectSummary {
  name: string;
  total_missions: number;
  completed_missions: number;
  in_progress_missions: number;
  progress_percentage: number;
}

export interface RoadmapResponse {
  roadmap: Roadmap | null;
  available_subjects: RoadmapSubjectSummary[];
  active_subject: string | null;
}
