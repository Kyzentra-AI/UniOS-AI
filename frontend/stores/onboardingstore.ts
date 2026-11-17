
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import type { OnboardingRawData } from '@/types/onboarding';

export type AcademicStatus =
  | 'BACHELOR'
  | 'MASTER'
  | 'RECENT_GRADUATE';

export interface EducationData {
  academicStatus: AcademicStatus | '';
  university: string;
  degreeProgram: string;
  domain: string;
  currentYear: string;
  subjects: string[];
  graduationYear: string;
  degree: string;
}

export interface CareerGoalsData {
  primaryGoal: string;
  targetSkills: string[];
}

export interface SkillsData {
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

export interface PreferencesData {
  dailyStudyHours: DailyStudyHours | '';
  learningDepth: LearningDepth | '';
}

interface OnboardingState {
  currentStep: number;
  education: EducationData;
  careerGoals: CareerGoalsData;
  skills: SkillsData;
  preferences: PreferencesData;

  setCurrentStep: (step: number) => void;
  setEducation: (data: Partial<EducationData>) => void;
  setCareerGoals: (data: Partial<CareerGoalsData>) => void;
  setSkills: (data: Partial<SkillsData>) => void;
  setPreferences: (data: Partial<PreferencesData>) => void;

  hydrateFromBackend: (data: OnboardingRawData) => void;
  resetOnboarding: () => void;
}

interface OnboardingDraft {
  version: 1;
  currentStep: number;
  education: EducationData;
  careerGoals: CareerGoalsData;
  skills: SkillsData;
  preferences: PreferencesData;
  savedAt: number;
}

export const ONBOARDING_DRAFT_KEY =
  'unios_onboarding_draft';

const initialEducation: EducationData = {
  academicStatus: '',
  university: '',
  degreeProgram: '',
  domain: '',
  currentYear: '',
  subjects: [],
  graduationYear: '',
  degree: '',
};

const initialCareerGoals: CareerGoalsData = {
  primaryGoal: '',
  targetSkills: [],
};

const initialSkills: SkillsData = {
  skills: [],
  projects: [],
  research: '',
  experience: '',
};

const initialPreferences: PreferencesData = {
  dailyStudyHours: '',
  learningDepth: '',
};

let hasRestoredSessionDraft = false;

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set) => ({
      currentStep: 1,

      education: { ...initialEducation },
      careerGoals: { ...initialCareerGoals },
      skills: { ...initialSkills },
      preferences: { ...initialPreferences },

      setCurrentStep: (step) =>
        set({
          currentStep: Math.min(Math.max(step, 1), 6),
        }),

      setEducation: (data) =>
        set((state) => ({
          education: {
            ...state.education,
            ...data,
          },
        })),

      setCareerGoals: (data) =>
        set((state) => ({
          careerGoals: {
            ...state.careerGoals,
            ...data,
          },
        })),

      setSkills: (data) =>
        set((state) => ({
          skills: {
            ...state.skills,
            ...data,
          },
        })),

      setPreferences: (data) =>
        set((state) => ({
          preferences: {
            ...state.preferences,
            ...data,
          },
        })),

      hydrateFromBackend: (data) => {
        // A valid session draft takes priority over backend hydration.
        if (hasRestoredSessionDraft) {
          return;
        }

        set({
          education: {
            academicStatus:
              data.academic_profile.academic_status ?? '',
            university:
              data.academic_profile.university ?? '',
            degreeProgram:
              data.academic_profile.degree_program ?? '',
            domain:
              data.academic_profile.domain ?? '',
            currentYear:
              data.academic_profile.current_year ?? '',
            subjects:
              data.academic_profile.subjects ?? [],
            graduationYear:
              data.academic_profile.graduation_year
                ? String(data.academic_profile.graduation_year)
                : '',
            degree:
              data.academic_profile.degree_program ?? '',
          },

          careerGoals: {
            primaryGoal:
              data.learner_profile.primary_goal ?? '',
            targetSkills:
              data.learner_profile.target_skills ?? [],
          },

          skills: {
            skills:
              data.learner_profile.skills ?? [],
            projects:
              data.learner_profile.projects ?? [],
            research:
              data.learner_profile.research ?? '',
            experience:
              data.learner_profile.experience ?? '',
          },

          preferences: {
            dailyStudyHours:
              data.learning_preferences.daily_study_hours ?? '',
            learningDepth:
              data.learning_preferences.learning_depth ?? '',
          },
        });
      },

      resetOnboarding: () =>
        set({
          currentStep: 1,
          education: { ...initialEducation },
          careerGoals: { ...initialCareerGoals },
          skills: { ...initialSkills },
          preferences: { ...initialPreferences },
        }),
    }),
    {
      name: 'unios-onboarding',
    }
  )
);

// Save the current onboarding state to sessionStorage.
export function saveOnboardingDraft(): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const state = useOnboardingStore.getState();

    const draft: OnboardingDraft = {
      version: 1,
      currentStep: state.currentStep,
      education: state.education,
      careerGoals: state.careerGoals,
      skills: state.skills,
      preferences: state.preferences,
      savedAt: Date.now(),
    };

    window.sessionStorage.setItem(
      ONBOARDING_DRAFT_KEY,
      JSON.stringify(draft)
    );
  } catch (error) {
    console.error(
      'Unable to save onboarding session draft:',
      error
    );
  }
}

// Restore a previously saved onboarding session draft.
export function restoreOnboardingDraft(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }

  try {
    const storedDraft = window.sessionStorage.getItem(
      ONBOARDING_DRAFT_KEY
    );

    if (!storedDraft) {
      return false;
    }

    const draft = JSON.parse(storedDraft) as OnboardingDraft;

    if (
      draft.version !== 1 ||
      !draft.education ||
      !draft.careerGoals ||
      !draft.skills ||
      !draft.preferences
    ) {
      return false;
    }

    hasRestoredSessionDraft = true;

    useOnboardingStore.setState({
      currentStep: Math.min(
        Math.max(Number(draft.currentStep) || 1, 1),
        6
      ),

      education: {
        ...initialEducation,
        ...draft.education,
      },

      careerGoals: {
        ...initialCareerGoals,
        ...draft.careerGoals,
      },

      skills: {
        ...initialSkills,
        ...draft.skills,
      },

      preferences: {
        ...initialPreferences,
        ...draft.preferences,
      },
    });

    return true;
  } catch (error) {
    console.error(
      'Unable to restore onboarding session draft:',
      error
    );

    return false;
  }
}

// Clear the session draft after successful onboarding.
export function clearOnboardingDraft(): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    window.sessionStorage.removeItem(
      ONBOARDING_DRAFT_KEY
    );

    hasRestoredSessionDraft = false;
  } catch (error) {
    console.error(
      'Unable to clear onboarding session draft:',
      error
    );
  }
}

// Automatically keep the session draft synchronized with store updates.
if (typeof window !== 'undefined') {
  useOnboardingStore.subscribe(() => {
    saveOnboardingDraft();
  });

  // Restore an existing draft before onboarding pages consume the store.
  restoreOnboardingDraft();
}
