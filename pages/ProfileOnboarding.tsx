
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { useOnboardingStore } from '@/stores/onboardingstore';

export default function ProfileOnboarding() {
  const router = useRouter();

  const {
    education,
    careerGoals,
    skills,
    preferences,
    setCurrentStep,
  } = useOnboardingStore();

  useEffect(() => {
    setCurrentStep(5);
  }, [setCurrentStep]);

  const handleContinue = () => {
    setCurrentStep(6);
    router.push('/onboarding/mission');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Step 5 of 6
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Review your profile
          </h1>

          <p className="mt-2 text-[var(--text-secondary)]">
            Review the information you provided before starting
            your first mission.
          </p>
        </div>

        <div className="space-y-4">
          {/* Education */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
              Education
            </h2>

            <div className="space-y-2 text-sm text-[var(--text-secondary)]">
              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Status:
                </span>{' '}
                {education.academicStatus || 'Not provided'}
              </p>

              <p>
                <span className="font-medium text-[var(--text-label)]">
                  University:
                </span>{' '}
                {education.university || 'Not provided'}
              </p>

              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Degree:
                </span>{' '}
                {education.degreeProgram || 'Not provided'}
              </p>

              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Semester:
                </span>{' '}
                {education.semester || 'Not provided'}
              </p>

              {education.currentSubjects.length > 0 && (
                <p>
                  <span className="font-medium text-[var(--text-label)]">
                    Subjects:
                  </span>{' '}
                  {education.currentSubjects.join(', ')}
                </p>
              )}
            </div>
          </section>

          {/* Career Goals */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
              Career Goals
            </h2>

            <div className="space-y-2 text-sm text-[var(--text-secondary)]">
              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Primary Goal:
                </span>{' '}
                {careerGoals.primaryGoal || 'Not provided'}
              </p>

              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Target Roles:
                </span>{' '}
                {careerGoals.targetRoles.length > 0
                  ? careerGoals.targetRoles.join(', ')
                  : 'Not provided'}
              </p>

              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Industries:
                </span>{' '}
                {careerGoals.industries.length > 0
                  ? careerGoals.industries.join(', ')
                  : 'Not provided'}
              </p>
            </div>
          </section>

          {/* Skills */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
              Skills
            </h2>

            <div className="space-y-2 text-sm text-[var(--text-secondary)]">
              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Skills:
                </span>{' '}
                {skills.skills.length > 0
                  ? skills.skills.join(', ')
                  : 'Not provided'}
              </p>

              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Experience Level:
                </span>{' '}
                {skills.experienceLevel || 'Not provided'}
              </p>

              {skills.projects.length > 0 && (
                <p>
                  <span className="font-medium text-[var(--text-label)]">
                    Projects:
                  </span>{' '}
                  {skills.projects.join(', ')}
                </p>
              )}

              {skills.githubUrl && (
                <p>
                  <span className="font-medium text-[var(--text-label)]">
                    GitHub:
                  </span>{' '}
                  {skills.githubUrl}
                </p>
              )}

              {skills.portfolioUrl && (
                <p>
                  <span className="font-medium text-[var(--text-label)]">
                    Portfolio:
                  </span>{' '}
                  {skills.portfolioUrl}
                </p>
              )}
            </div>
          </section>

          {/* Preferences */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="mb-4 text-lg font-semibold text-[var(--text-primary)]">
              Learning Preferences
            </h2>

            <div className="space-y-2 text-sm text-[var(--text-secondary)]">
              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Language:
                </span>{' '}
                {preferences.language || 'Not provided'}
              </p>

              <p>
                <span className="font-medium text-[var(--text-label)]">
                  Learning Modes:
                </span>{' '}
                {preferences.learningModes.length > 0
                  ? preferences.learningModes.join(', ')
                  : 'Not provided'}
              </p>
            </div>
          </section>
        </div>

        <div className="mt-8 flex items-center justify-between border-t border-[var(--border)] pt-6">
          <button
            type="button"
            onClick={() =>
              router.push('/onboarding/preferences')
            }
            className="text-sm font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          >
            ← Back to preferences
          </button>

          <button
            type="button"
            onClick={handleContinue}
            className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)]"
          >
            Continue →
          </button>
        </div>
      </div>
    </div>
  );
}

