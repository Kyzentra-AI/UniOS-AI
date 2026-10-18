export type CompetitionType =
  | 'HACKATHON'
  | 'CODING_COMPETITION'
  | 'INNOVATION_CHALLENGE'
  | 'STUDENT_CHALLENGE'
  | 'CASE_COMPETITION'
  | 'RESEARCH_CHALLENGE'
  | 'OTHER';

export type CompetitionDomain =
  | 'AI_ML'
  | 'WEB_DEVELOPMENT'
  | 'DATA_SCIENCE'
  | 'CYBERSECURITY'
  | 'CLOUD_DEVOPS'
  | 'DESIGN'
  | 'BUSINESS'
  | 'ROBOTICS'
  | 'SUSTAINABILITY'
  | 'GENERAL';

export type CompetitionDifficulty = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'ALL_LEVELS';
export type CompetitionGoal =
  | 'LEARNING'
  | 'PORTFOLIO'
  | 'PRIZES'
  | 'NETWORKING'
  | 'RESEARCH'
  | 'CAREER'
  | 'SOCIAL_IMPACT';

export type EligibilityStatus = 'ELIGIBLE' | 'NOT_ELIGIBLE' | 'NEEDS_REVIEW' | 'UNKNOWN';
export type CompetitionStatus = 'UPCOMING' | 'OPEN' | 'CLOSING_SOON' | 'CLOSED' | 'ONGOING';

export interface CompetitionOrganizer {
  name: string;
  websiteUrl?: string | null;
  logoUrl?: string | null;
}

export interface CompetitionEligibility {
  summary: string;
  eligibleDegrees?: string[];
  eligibleYears?: string[];
  eligibleRegions?: string[];
  minimumTeamSize?: number | null;
  maximumTeamSize?: number | null;
  requiresTeam?: boolean;
  requirements?: string[];
  status?: EligibilityStatus;
  statusReason?: string | null;
}

export interface CompetitionRecord {
  id: string;
  title: string;
  slug?: string | null;
  type: CompetitionType;
  domain: CompetitionDomain;
  domains?: CompetitionDomain[];
  summary: string;
  description?: string | null;
  skills: string[];
  difficulty: CompetitionDifficulty;
  goals: CompetitionGoal[];
  status: CompetitionStatus;
  eligibility: CompetitionEligibility;
  organizer: CompetitionOrganizer;
  startsAt?: string | null;
  deadlineAt?: string | null;
  endsAt?: string | null;
  registrationUrl: string;
  informationUrl?: string | null;
  prizeSummary?: string | null;
  isRecommended?: boolean;
  recommendationReasons?: string[];
  createdAt?: string;
  updatedAt?: string;
}

export interface CompetitionFilters {
  search?: string;
  types?: CompetitionType[];
  domains?: CompetitionDomain[];
  skills?: string[];
  difficulty?: CompetitionDifficulty[];
  goals?: CompetitionGoal[];
  eligibility?: EligibilityStatus[];
  status?: CompetitionStatus[];
  deadlineBefore?: string;
  page?: number;
  pageSize?: number;
  sort?: 'deadline_asc' | 'newest' | 'recommended';
}

export interface CompetitionListResponse {
  items: CompetitionRecord[];
  total: number;
  page: number;
  pageSize: number;
}

export interface CompetitionDetailResponse {
  competition: CompetitionRecord;
}

export interface CompetitionProfileContext {
  degree?: string | null;
  studyYear?: string | null;
  domains?: CompetitionDomain[];
  skills?: string[];
  goals?: CompetitionGoal[];
  region?: string | null;
}

export interface CompetitionRecommendationResponse {
  items: CompetitionRecord[];
  contextUsed: string[];
  generatedAt?: string;
}

export interface ApiErrorResponse {
  code: string;
  message: string;
  details?: unknown;
  requestId?: string;
}
