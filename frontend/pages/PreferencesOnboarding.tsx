'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import {
  preferencesSchema,
  type PreferencesFormData,
} from '@/app/validations/onboarding';

import { useOnboardingStore } from '@/stores/onboardingstore';

const studyTimeOptions = [
  {
    value: 'LESS_THAN_1',
    label: 'Less than 1 hour',
  },
  {
    value: '1_2',
    label: '1–2 hours',
  },
  {
    value: '2_3',
    label: '2–3 hours',
  },
  {
    value: '3_4',
    label: '3–4 hours',
  },
  {
    value: '4_PLUS',
    label: '4+ hours',
  },
] as const;

const learningDepthOptions = [
  {
    value: 'QUICK',
    label: 'Quick',
    description: 'Concise explanations and key points',
  },
  {
    value: 'BALANCED',
    label: 'Balanced',
    description: 'Concepts with examples and practical context',
  },
  {
    value: 'DEEP',
    label: 'Deep',
    description:
      'Detailed explanations, reasoning, examples and edge cases',
  },
] as const;

export default function PreferencesOnboarding() {
  const router = useRouter();

  const {
    preferences,
    setPreferences,
    setCurrentStep,
  } = useOnboardingStore();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<PreferencesFormData>({
    resolver: zodResolver(preferencesSchema),
    defaultValues: {
      dailyStudyHours: preferences?.dailyStudyHours || '',
      learningDepth: preferences?.learningDepth || '',
    },
  });

  const dailyStudyHours = watch('dailyStudyHours');
  const learningDepth = watch('learningDepth');

  useEffect(() => {
    if (!preferences) return;

    setValue(
      'dailyStudyHours',
      preferences.dailyStudyHours || ''
    );

    setValue(
      'learningDepth',
      preferences.learningDepth || ''
    );
  }, [preferences, setValue]);

  const onSubmit = (data: PreferencesFormData) => {
    setPreferences({
      dailyStudyHours: data.dailyStudyHours,
      learningDepth: data.learningDepth,
    });

    setCurrentStep(5);
    router.push('/onboarding/profile');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">

        {/* Header */}
        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Step 4 of 6
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Set your learning preferences
          </h1>

          <p className="mt-2 text-[var(--text-secondary)]">
            Tell us how much time you can study and how deeply you want to
            learn.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>

          {/* Daily Study Time */}
          <section className="mb-8 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <div className="mb-5">
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                How much time can you study each day?
              </h2>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                We&apos;ll use this to adjust your daily learning plan.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {studyTimeOptions.map((option) => {
                const selected =
                  dailyStudyHours === option.value;

                return (
                  <label
                    key={option.value}
                    className={`cursor-pointer rounded-xl border p-4 transition ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--background)]'
                        : 'border-[var(--border)] hover:border-[var(--primary)]'
                    }`}
                  >
                    <input
                      type="radio"
                      value={option.value}
                      {...register('dailyStudyHours')}
                      className="sr-only"
                    />

                    <div className="flex items-center justify-between">
                      <span className="font-medium text-[var(--text-primary)]">
                        {option.label}
                      </span>

                      <div
                        className={`h-4 w-4 rounded-full border ${
                          selected
                            ? 'border-[var(--primary)] bg-[var(--primary)]'
                            : 'border-[var(--border)]'
                        }`}
                      />
                    </div>
                  </label>
                );
              })}
            </div>

            {errors.dailyStudyHours && (
              <p className="mt-3 text-sm text-red-500">
                {errors.dailyStudyHours.message}
              </p>
            )}
          </section>

          {/* Learning Depth */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <div className="mb-5">
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                How deeply do you want to learn?
              </h2>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                This helps us decide how detailed your explanations and
                learning material should be.
              </p>
            </div>

            <div className="space-y-3">
              {learningDepthOptions.map((option) => {
                const selected =
                  learningDepth === option.value;

                return (
                  <label
                    key={option.value}
                    className={`block cursor-pointer rounded-xl border p-4 transition ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--background)]'
                        : 'border-[var(--border)] hover:border-[var(--primary)]'
                    }`}
                  >
                    <input
                      type="radio"
                      value={option.value}
                      {...register('learningDepth')}
                      className="sr-only"
                    />

                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-medium text-[var(--text-primary)]">
                          {option.label}
                        </h3>

                        <p className="mt-1 text-sm text-[var(--text-secondary)]">
                          {option.description}
                        </p>
                      </div>

                      <div
                        className={`mt-1 h-4 w-4 shrink-0 rounded-full border ${
                          selected
                            ? 'border-[var(--primary)] bg-[var(--primary)]'
                            : 'border-[var(--border)]'
                        }`}
                      />
                    </div>
                  </label>
                );
              })}
            </div>

            {errors.learningDepth && (
              <p className="mt-3 text-sm text-red-500">
                {errors.learningDepth.message}
              </p>
            )}
          </section>

          {/* Navigation */}
          <div className="mt-8 flex items-center justify-between border-t border-[var(--border)] pt-6">
            <button
              type="button"
              onClick={() => router.push('/onboarding/skills')}
              className="text-sm font-semibold text-[var(--text-secondary)] transition hover:text-[var(--text-primary)]"
            >
              ← Back
            </button>

            <button
              type="submit"
              className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)]"
            >
              Continue →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}