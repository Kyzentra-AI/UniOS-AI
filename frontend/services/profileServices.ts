import { apiRequest } from "@/lib/api";
import type { StudentProfile } from "@/types/profile";

interface OnboardingResponse {
  status: string;
  raw_data: {
    learner_profile: {
      profile_id?: string;
      learner_profile_id?: string;
      user_id?: string;
      primary_goal?: string | null;
      target_skills?: string[] | null;
      skills?: string[] | null;
      projects?: string[] | null;
      research?: string | null;
      experience?: string | null;
      created_at?: string;
      updated_at?: string;
    };
    academic_profile: {
      academic_status?: StudentProfile["education"]["academic_status"];
      university?: string | null;
      degree_program?: string | null;
      domain?: string | null;
      current_year?: string | null;
      graduation_year?: number | null;
      subjects?: string[] | null;
    };
    learning_preferences: {
      daily_study_hours?: StudentProfile["preferences"]["daily_study_hours"];
      learning_depth?: StudentProfile["preferences"]["learning_depth"];
    };
  };
  context: Record<string, unknown>;
}

export const getProfile = async (): Promise<StudentProfile> => {
  const response = await apiRequest<OnboardingResponse>(
    "/api/v1/onboarding"
  );

  const { learner_profile, academic_profile, learning_preferences } =
    response.raw_data;

  return {
    profile_id:
      learner_profile.profile_id ??
      learner_profile.learner_profile_id ??
      "",
    user_id: learner_profile.user_id ?? "",

    education: {
      academic_status: academic_profile.academic_status ?? "BACHELOR",
      university: academic_profile.university ?? undefined,
      degree_program: academic_profile.degree_program ?? undefined,
      domain: academic_profile.domain ?? "",
      current_year: academic_profile.current_year ?? undefined,
      graduation_year:
        academic_profile.graduation_year?.toString() ?? undefined,
      subjects: academic_profile.subjects ?? [],
    },

    career_goals: {
      primary_goal: learner_profile.primary_goal ?? "",
      target_skills: learner_profile.target_skills ?? [],
    },

    skills: {
      skills: learner_profile.skills ?? [],
      projects: learner_profile.projects ?? [],
      research: learner_profile.research ?? "",
      experience: learner_profile.experience ?? "",
    },

    preferences: {
      daily_study_hours:
        learning_preferences.daily_study_hours ?? "LESS_THAN_1",
      learning_depth: learning_preferences.learning_depth ?? "BALANCED",
    },

    created_at: learner_profile.created_at ?? "",
    updated_at: learner_profile.updated_at ?? "",
    explicit_directives: [],
  };
};