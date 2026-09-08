
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type AcademicStatus =
  | 'BACHELOR'
  | 'MASTER'
  | 'RECENT_GRADUATE';

export type ExperienceLevel =
  | 'BEGINNER'
  | 'INTERMEDIATE'
  | 'ADVANCED';

export type LearningLanguage =
  | 'ENGLISH'
  | 'HINDI'
  | 'MARATHI'
  | 'KANNADA'
  | 'TAMIL'
  | 'BENGALI'
  | 'TELUGU';

export type LearningMode =
  | 'VISUAL'
  | 'STORY'
  | 'VOICE'
  | 'TEXT';

export interface EducationData {
  academicStatus: AcademicStatus | '';

  university: string;
  degreeProgram: string;
  semester: string;
  currentSubjects: string[];

  graduationStatus: string;
  degreeBackground: string;
  passoutYear: string;
}

export interface CareerGoalsData {
  primaryGoal: string;
  targetRoles: string[];
  industries: string[];
}

export interface SkillsData {
  skills: string[];
  experienceLevel: ExperienceLevel | '';
  projects: string[];
  portfolioUrl: string;
  githubUrl: string;
}

export interface PreferencesData {
  language: LearningLanguage | '';
  learningModes: LearningMode[];
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
  semester: '',
  currentSubjects: [],

  graduationStatus: '',
  degreeBackground: '',
  passoutYear: '',
};

const initialCareerGoals: CareerGoalsData = {
  primaryGoal: '',
  targetRoles: [],
  industries: [],
};

const initialSkills: SkillsData = {
  skills: [],
  experienceLevel: '',
  projects: [],
  portfolioUrl: '',
  githubUrl: '',
};

const initialPreferences: PreferencesData = {
  language: '',
  learningModes: [],
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
