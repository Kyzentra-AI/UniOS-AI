export interface StudentProfile {
  profile_id: string;
  user_id: string;

  education: EducationProfile;
  career_goals: CareerGoalsProfile;
  skills: SkillsProfile;
  preferences: PreferencesProfile;

  created_at: string;
  updated_at: string;

  explicit_directives: string[];
}

export interface EducationProfile {
  academic_status:
    | 'BACHELOR'
    | 'MASTER'
    | 'RECENT_GRADUATE';

  university?: string;
  degree_program?: string;
  domain: string;
  current_year?: string;
  subjects?: string[];

  degree?: string;
  graduation_year?: string;
}

export interface CareerGoalsProfile {
  primary_goal: string;
  target_skills: string[];
}

export interface SkillsProfile {
  skills: string[];
  projects: string[];
  research: string;
  experience: string;
}

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

export interface PreferencesProfile {
  daily_study_hours: DailyStudyHours;
  learning_depth: LearningDepth;
}

export interface StudentProfileCreatePayload {
  education: EducationProfile;
  career_goals: CareerGoalsProfile;
  skills: SkillsProfile;
  preferences: PreferencesProfile;
}

export interface ExplicitDirectiveCreatePayload {
  directive_text: string;
}

export interface ExplicitDirective {
  directive_id: string;
  user_id: string;
  directive_text: string;
  is_active: boolean;
  created_at: string;
}