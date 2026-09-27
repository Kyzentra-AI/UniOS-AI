export interface ActiveFrictionPoint {
  concept: string;
  error_frequency: number;
  last_observed: string;
}

export interface UserPreferencesPayload {
  language: string;
  delivery_mode: string;
  code_language: string;
}

export interface ContextPayload {
  student_id: string;
  preferences: UserPreferencesPayload;
  mastery_summary: Record<string, number>;
  active_friction_points: ActiveFrictionPoint[];
  explicit_directives: string[];
}

export interface MemoryLog {
  memory_id: string;
  user_id: string;
  concept: string;
  error_frequency: number;
  last_observed: string;
  is_archived: boolean;
}

export interface MemoryLogCreatePayload {
  concept: string;
  error_type?: string;
  error_frequency_increment?: number;
}

export interface MemoryResetPayload {
  reset_scope: string;
  concept?: string;
}

export interface ApiMessageResponse {
  message: string;
}