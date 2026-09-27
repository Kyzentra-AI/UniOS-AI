export type MissionStatus =
  | 'PENDING'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'DEFERRED'
  | 'SKIPPED';

export type MissionType =
  | 'LEARNING'
  | 'REVISION'
  | 'ASSIGNMENT'
  | 'PRACTICAL'
  | 'ARTIFACT'
  | 'CAREER';

export interface Mission {
  id: string;
  roadmap_id: string;
  title: string;
  description?: string | null;
  mission_type: MissionType;
  subject?: string | null;
  priority?: string | null;
  estimated_minutes?: number | null;
  week?: number | null;
  sequence?: number | null;
  status: MissionStatus;
}

export type MissionResponse = Mission;

export type CompleteMissionResponse = Mission;