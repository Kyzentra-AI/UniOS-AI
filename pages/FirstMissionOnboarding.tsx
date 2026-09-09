
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { useOnboardingStore } from '@/stores/onboardingstore';

export default function FirstMissionOnboarding() {
  const router = useRouter();

  const {
    careerGoals,
    skills,
    setCurrentStep,
  } = useOnboardingStore();

  useEffect(() => {
    setCurrentStep(6);
  }, [setCurrentStep]);

  const handleBack = () => {
    setCurrentStep(5);
    router.push('/onboarding/profile');
  };

  const handleFinish = () => {
    setCurrentStep(6);
    router.push('/dashboard');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm sm:p-8">
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--primary-soft)] text-2xl">
              🚀
            </div>

            <h1 className="text-2xl font-bold text-[var(--text-primary)] sm:text-3xl">
              Your first mission awaits
            </h1>

            <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
              Your profile is ready. Based on your goals and skills, UniOS
              can now help you start working toward your next milestone.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
                Career Goal
              </p>

              <p className="mt-2 text-base font-semibold text-[var(--text-primary)]">
                {careerGoals.primaryGoal || 'Not specified'}
              </p>
            </div>

            <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
                Experience Level
              </p>

              <p className="mt-2 text-base font-semibold capitalize text-[var(--text-primary)]">
                {skills.experienceLevel
                  ? skills.experienceLevel.toLowerCase()
                  : 'Not specified'}
              </p>
            </div>
          </div>

          <div className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
              Your Skills
            </p>

            {skills.skills.length > 0 ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {skills.skills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full bg-[var(--primary-soft)] px-3 py-1.5 text-sm font-medium text-[var(--primary)]"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="mt-2 text-sm text-[var(--text-muted)]">
                No skills added yet.
              </p>
            )}
          </div>

          <div className="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
            <button
              type="button"
              onClick={handleBack}
              className="rounded-xl border border-[var(--border)] px-5 py-3 text-sm font-semibold text-[var(--text-primary)] transition-colors hover:bg-[var(--surface-muted)]"
            >
              Back
            </button>

            <button
              type="button"
              onClick={handleFinish}
              className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-[var(--primary-hover)]"
            >
              Start My First Mission
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
