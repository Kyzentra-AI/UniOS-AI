import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type AcademicStatus =
  | 'BACHELOR'
  | 'MASTER'
  | 'RECENT_GRADUATE';

export interface EducationData {
  academicStatus: AcademicStatus | '';

  // Bachelor / Master
  university: string;
  degreeProgram: string;
  domain: string;
  currentYear: string;
  subjects: string[];

  // Recent Graduate
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

  setEducation: (
    data: Partial<EducationData>
  ) => void;

  setCareerGoals: (
    data: Partial<CareerGoalsData>
  ) => void;

  setSkills: (
    data: Partial<SkillsData>
  ) => void;

  setPreferences: (
    data: Partial<PreferencesData>
  ) => void;

  resetOnboarding: () => void;
}

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

export const useOnboardingStore =
  create<OnboardingState>()(
    persist(
      (set) => ({
        currentStep: 1,

        education: {
          ...initialEducation,
        },

        careerGoals: {
          ...initialCareerGoals,
        },

        skills: {
          ...initialSkills,
        },

        preferences: {
          ...initialPreferences,
        },

        setCurrentStep: (step) =>
          set({
            currentStep: Math.min(
              Math.max(step, 1),
              6
            ),
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

        resetOnboarding: () =>
          set({
            currentStep: 1,

            education: {
              ...initialEducation,
            },

            careerGoals: {
              ...initialCareerGoals,
            },

            skills: {
              ...initialSkills,
            },

            preferences: {
              ...initialPreferences,
            },
          }),
      }),
      {
        name: 'unios-onboarding',
      }
    )
  );