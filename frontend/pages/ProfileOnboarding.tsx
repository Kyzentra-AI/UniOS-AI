
'use client';

import { useRouter } from 'next/navigation';

import { useOnboardingStore } from '@/stores/onboardingstore';
import { useOnboarding } from '@/hooks/useOnboarding';

const academicStatusLabels: Record<string, string> = {
  BACHELOR: 'Bachelor',
  MASTER: 'Master',
  RECENT_GRADUATE: 'Recent Graduate',
};

const formatStudyHours = (value: string) => {
  const labels: Record<string, string> = {
    LESS_THAN_1: 'Less than 1 hour',
    '1_2': '1–2 hours',
    '2_3': '2–3 hours',
    '3_4': '3–4 hours',
    '4_PLUS': '4+ hours',
  };

  return labels[value] || value;
};

const learningDepthLabels: Record<string, string> = {
  QUICK: 'Quick',
  BALANCED: 'Balanced',
  DEEP: 'Deep',
};

export default function ProfileOnboarding() {
  const router = useRouter();

  const {
    education,
    careerGoals,
    skills,
    preferences,
    setCurrentStep,
  } = useOnboardingStore();

  const {
    onboarding,
    initializeOnboarding,
    updateOnboarding,
    isLoading: isOnboardingLoading,
    isSaving,
    saveError,
  } = useOnboarding();

  const handleContinue = async () => {
    // Wait until the existing onboarding state has been loaded.
    if (isOnboardingLoading) {
      return;
    }

    if (!education.academicStatus) {
      console.error('Academic status is missing.');
      return;
    }

    if (!preferences.dailyStudyHours) {
      console.error('Daily study hours are missing.');
      return;
    }

    if (!preferences.learningDepth) {
      console.error('Learning depth is missing.');
      return;
    }

    const payload = {
      learner_profile: {
        primary_goal: careerGoals.primaryGoal,
        target_skills: careerGoals.targetSkills,
        skills: skills.skills,
        projects: skills.projects,
        research: skills.research || null,
        experience: skills.experience || null,
      },

      academic_profile: {
        academic_status: education.academicStatus,

        university:
          education.academicStatus === 'RECENT_GRADUATE'
            ? null
            : education.university,

        degree_program:
          education.academicStatus === 'RECENT_GRADUATE'
            ? education.degree
            : education.degreeProgram,

        domain: education.domain,

        current_year:
          education.academicStatus === 'BACHELOR' ||
          education.academicStatus === 'MASTER'
            ? education.currentYear
            : null,

        graduation_year:
          education.academicStatus === 'RECENT_GRADUATE'
            ? Number(education.graduationYear)
            : null,

        subjects:
          education.academicStatus === 'BACHELOR' ||
          education.academicStatus === 'MASTER'
            ? education.subjects
            : [],
      },

      learning_preferences: {
        daily_study_hours: preferences.dailyStudyHours,
        learning_depth: preferences.learningDepth,
      },
    };

    try {
      const onboardingStatus = onboarding?.status as string | undefined;

      if (onboardingStatus === 'NOT_STARTED') {
        await initializeOnboarding(payload);
      } else if (
        onboardingStatus === 'IN_PROGRESS' ||
        onboardingStatus === 'KIE_ANALYZING' ||
        onboardingStatus === 'KIE_RESOLVING'
      ) {
        await updateOnboarding(payload);
      } else if (onboardingStatus === 'COMPLETED') {
        console.error('Onboarding is already completed.');
        return;
      } else {
        console.error(
          'Unexpected onboarding status:',
          onboardingStatus
        );
        return;
      }

      setCurrentStep(6);
      router.push('/onboarding/assessment');
    } catch (error) {
      console.error(
        'Failed to save onboarding:',
        error
      );
    }
  };

  const isStudent =
    education.academicStatus === 'BACHELOR' ||
    education.academicStatus === 'MASTER';


  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">

        {/* Header */}
        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Step 5 of 6
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Review your profile
          </h1>

          <p className="mt-2 text-[var(--text-secondary)]">
            Review the information you provided before we prepare your
            learning assessment.
          </p>
        </div>

        <div className="space-y-4">

          {/* Education */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="mb-5 text-lg font-semibold text-[var(--text-primary)]">
              Education
            </h2>

            <div className="space-y-3 text-sm">

              <p className="text-[var(--text-secondary)]">
                <span className="font-medium text-[var(--text-label)]">
                  Academic Status:
                </span>{' '}
                {academicStatusLabels[education.academicStatus] ||
                  education.academicStatus ||
                  'Not provided'}
              </p>

              {isStudent ? (
                <>
                  <p className="text-[var(--text-secondary)]">
                    <span className="font-medium text-[var(--text-label)]">
                      University:
                    </span>{' '}
                    {education.university || 'Not provided'}
                  </p>

                  <p className="text-[var(--text-secondary)]">
                    <span className="font-medium text-[var(--text-label)]">
                      Degree Program:
                    </span>{' '}
                    {education.degreeProgram || 'Not provided'}
                  </p>

                  <p className="text-[var(--text-secondary)]">
                    <span className="font-medium text-[var(--text-label)]">
                      Domain:
                    </span>{' '}
                    {education.domain || 'Not provided'}
                  </p>

                  <p className="text-[var(--text-secondary)]">
                    <span className="font-medium text-[var(--text-label)]">
                      Current Year:
                    </span>{' '}
                    {education.currentYear || 'Not provided'}
                  </p>

                  <div>
                    <span className="font-medium text-[var(--text-label)]">
                      Subjects:
                    </span>

                    {education.subjects?.length > 0 ? (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {education.subjects.map((subject) => (
                          <span
                            key={subject}
                            className="rounded-full bg-[var(--background)] px-3 py-1 text-xs text-[var(--text-secondary)]"
                          >
                            {subject}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="ml-1 text-[var(--text-secondary)]">
                        Not provided
                      </span>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <p className="text-[var(--text-secondary)]">
                    <span className="font-medium text-[var(--text-label)]">
                      Degree:
                    </span>{' '}
                    {education.degree || 'Not provided'}
                  </p>

                  <p className="text-[var(--text-secondary)]">
                    <span className="font-medium text-[var(--text-label)]">
                      Domain:
                    </span>{' '}
                    {education.domain || 'Not provided'}
                  </p>

                  <p className="text-[var(--text-secondary)]">
                    <span className="font-medium text-[var(--text-label)]">
                      Graduation Year:
                    </span>{' '}
                    {education.graduationYear || 'Not provided'}
                  </p>
                </>
              )}
            </div>
          </section>

          {/* Career Goals */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="mb-5 text-lg font-semibold text-[var(--text-primary)]">
              Career Goals
            </h2>

            <div className="space-y-4 text-sm">

              <div>
                <p className="font-medium text-[var(--text-label)]">
                  Primary Goal
                </p>

                <p className="mt-1 leading-6 text-[var(--text-secondary)]">
                  {careerGoals.primaryGoal || 'Not provided'}
                </p>
              </div>

              <div>
                <p className="font-medium text-[var(--text-label)]">
                  Target Skills
                </p>

                {careerGoals.targetSkills?.length > 0 ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {careerGoals.targetSkills.map((skill) => (
                      <span
                        key={skill}
                        className="rounded-full bg-[var(--background)] px-3 py-1 text-xs text-[var(--text-secondary)]"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mt-1 text-[var(--text-secondary)]">
                    Not provided
                  </p>
                )}
              </div>
            </div>
          </section>

          {/* Existing Skills */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="mb-5 text-lg font-semibold text-[var(--text-primary)]">
              Skills & Experience
            </h2>

            <div className="space-y-5 text-sm">

              <div>
                <p className="font-medium text-[var(--text-label)]">
                  Skills
                </p>

                {skills.skills?.length > 0 ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {skills.skills.map((skill) => (
                      <span
                        key={skill}
                        className="rounded-full bg-[var(--background)] px-3 py-1 text-xs text-[var(--text-secondary)]"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mt-1 text-[var(--text-secondary)]">
                    Not provided
                  </p>
                )}
              </div>

              <div>
                <p className="font-medium text-[var(--text-label)]">
                  Projects
                </p>

                {skills.projects?.length > 0 ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {skills.projects.map((project) => (
                      <span
                        key={project}
                        className="rounded-full bg-[var(--background)] px-3 py-1 text-xs text-[var(--text-secondary)]"
                      >
                        {project}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mt-1 text-[var(--text-secondary)]">
                    None provided
                  </p>
                )}
              </div>

              <div>
                <p className="font-medium text-[var(--text-label)]">
                  Research
                </p>

                <p className="mt-1 leading-6 text-[var(--text-secondary)]">
                  {skills.research || 'None provided'}
                </p>
              </div>

              <div>
                <p className="font-medium text-[var(--text-label)]">
                  Experience
                </p>

                <p className="mt-1 leading-6 text-[var(--text-secondary)]">
                  {skills.experience || 'None provided'}
                </p>
              </div>
            </div>
          </section>

          {/* Preferences */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="mb-5 text-lg font-semibold text-[var(--text-primary)]">
              Learning Preferences
            </h2>

            <div className="space-y-3 text-sm">

              <p className="text-[var(--text-secondary)]">
                <span className="font-medium text-[var(--text-label)]">
                  Daily Study Time:
                </span>{' '}
                {formatStudyHours(preferences.dailyStudyHours) ||
                  'Not provided'}
              </p>

              <p className="text-[var(--text-secondary)]">
                <span className="font-medium text-[var(--text-label)]">
                  Learning Depth:
                </span>{' '}
                {learningDepthLabels[preferences.learningDepth] ||
                  preferences.learningDepth ||
                  'Not provided'}
              </p>

            </div>
          </section>
        </div>

        {/* Backend error */}
        {saveError && (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
            {saveError instanceof Error
              ? saveError.message
              : 'Failed to save your profile. Please try again.'}
          </div>
        )}

        {/* Actions */}
        <div className="mt-8 flex items-center justify-between border-t border-[var(--border)] pt-6">

          <button
            type="button"
            onClick={() =>
              router.push('/onboarding/preferences')
            }
            disabled={isSaving}
            className="text-sm font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            ← Back
          </button>

          <button
            type="button"
            onClick={handleContinue}
            disabled={isSaving}
            className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSaving
              ? 'Preparing assessment...'
              : 'Confirm & Continue →'}
          </button>

        </div>

      </div>
    </div>
  );
}