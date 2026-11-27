
export type FileCategory =
  | 'ALL'
  | 'SYLLABUS'
  | 'BUILD_ARTIFACT'
  | 'RESUME'
  | 'ATS';

export type DownloadableFileCategory =
  | 'SYLLABUS'
  | 'BUILD_ARTIFACT'
  | 'RESUME';

export interface SettingsAccountProfile {
  userId: string;
  fullName: string;
  email: string;
  emailVerified: boolean;
  phone?: string | null;
  bio?: string | null;
  avatarUrl?: string | null;
  timezone: string;
  registrationDate?: string | null;
  lastLogin?: string | null;
}

export interface SettingsLearnerProfile {
  learnerId: string;
  primaryGoal?: string | null;
  targetSkills: string[];
  skills: string[];
  experience?: string | null;
  research?: string | null;
  onboardingStatus: string;
}

export interface SettingsAcademicProfile {
  academicStatus?: string | null;
  university?: string | null;
  degreeProgram?: string | null;
  domain?: string | null;
  currentYear?: string | null;
  graduationYear?: number | null;
  subjects: string[];
}

export interface SettingsLearningPreferences {
  dailyStudyHours?: string | null;
  learningDepth?: string | null;
}

export interface SettingsProfile {
  account: SettingsAccountProfile;
  learner: SettingsLearnerProfile;
  academic: SettingsAcademicProfile;
  learningPreferences: SettingsLearningPreferences;
}

export interface SettingsProfilePatch {
  account?: {
    fullName?: string;
    phone?: string | null;
    bio?: string | null;
    timezone?: string;
  };
  learner?: {
    primaryGoal?: string | null;
    targetSkills?: string[];
    skills?: string[];
    experience?: string | null;
    research?: string | null;
  };
  academic?: {
    academicStatus?: string | null;
    university?: string | null;
    degreeProgram?: string | null;
    domain?: string | null;
    currentYear?: string | null;
    graduationYear?: number | null;
    subjects?: string[];
  };
  learningPreferences?: {
    dailyStudyHours?: string | null;
    learningDepth?: string | null;
  };
}

export interface SettingsAvatarResponse {
  avatarUrl: string;
}

export interface SettingsAIContext {
  planTier: string;
  aiPersonalizationEnabled: boolean;
  activeSyllabus?: Record<string, unknown> | null;
  activeRoadmap?: Record<string, unknown> | null;
  memorySummary?: Record<string, unknown> | null;
  [key: string]: unknown;
}

export interface SettingsFile {
  id: string;
  category: Exclude<FileCategory, 'ALL'>;
  fileName: string;
  fileType?: string | null;
  fileSize?: number | null;
  status?: string | null;
  subject?: string | null;
  projectTitle?: string | null;
  artifactTitle?: string | null;
  version?: number | null;
  overallScore?: number | null;
  storageKey?: string | null;
  downloadEndpoint: string;
  createdAt?: string | null;
}

export interface SettingsFilesResponse {
  files: SettingsFile[];
  total: number;
  countsByCategory: Record<string, number>;
}

export interface SettingsFileDownloadResponse {
  url: string;
  expiresIn: number | null;
  isApiExport: boolean;
  fileName: string;
}

export interface SettingsPreferences {
  emailNotifications: boolean;
  studyReminders: boolean;
  productUpdates: boolean;
  aiPersonalizationEnabled: boolean;
  updatedAt?: string | null;
}

export type SettingsPreferencesPatch = Partial<
  Pick<
    SettingsPreferences,
    | 'emailNotifications'
    | 'studyReminders'
    | 'productUpdates'
    | 'aiPersonalizationEnabled'
  >
>;

export interface SettingsAccount {
  userId: string;
  email: string;
  emailVerified: boolean;
  mfaEnabled: boolean;
  authProviders: string[];
  hasPasswordAuth: boolean;
  activeSubscription?: {
    currentPlan: string;
    billingCycle?: string | null;
    status: string;
    currentPeriodEnd?: string | null;
    daysRemaining?: number | null;
  } | null;
}

export interface DeleteAccountPayload {
  confirmationText: 'DELETE';
  currentPassword?: string;
  totpCode?: string;
}

export interface SettingsMessageResponse {
  message: string;
}
