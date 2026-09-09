
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import {
  preferencesSchema,
  type PreferencesFormData,
} from '@/app/validations/onboarding';

import {
  useOnboardingStore,
  type LearningLanguage,
  type LearningMode,
} from '@/stores/onboardingstore';

const languages: {
  value: LearningLanguage;
  label: string;
}[] = [
  { value: 'ENGLISH', label: 'English' },
  { value: 'HINDI', label: 'Hindi' },
  { value: 'MARATHI', label: 'Marathi' },
  { value: 'KANNADA', label: 'Kannada' },
  { value: 'TAMIL', label: 'Tamil' },
  { value: 'BENGALI', label: 'Bengali' },
  { value: 'TELUGU', label: 'Telugu' },
];

const learningModes: {
  value: LearningMode;
  label: string;
  description: string;
}[] = [
  {
    value: 'VISUAL',
    label: 'Visual',
    description: 'Learn through diagrams, visuals and examples.',
  },
  {
    value: 'STORY',
    label: 'Story-based',
    description: 'Learn concepts through stories and real situations.',
  },
  {
    value: 'VOICE',
    label: 'Voice',
    description: 'Learn through spoken explanations.',
  },
  {
    value: 'TEXT',
    label: 'Text',
    description: 'Learn through written explanations and notes.',
  },
];

export default function PreferencesOnboarding() {
  const router = useRouter();

  const {
    preferences,
    setPreferences,
    setCurrentStep,
  } = useOnboardingStore();

  const {
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<PreferencesFormData>({
    resolver: zodResolver(preferencesSchema),
    defaultValues: {
      language:
        preferences.language === ''
          ? undefined
          : preferences.language,
      learningModes: preferences.learningModes,
    },
  });

  const selectedLanguage = watch('language');
  const selectedModes = watch('learningModes');

  useEffect(() => {
    setCurrentStep(4);
  }, [setCurrentStep]);

  const selectLanguage = (language: LearningLanguage) => {
    setValue('language', language, {
      shouldValidate: true,
    });
  };

  const toggleLearningMode = (mode: LearningMode) => {
    const currentModes = selectedModes ?? [];

    const updatedModes = currentModes.includes(mode)
      ? currentModes.filter((item) => item !== mode)
      : [...currentModes, mode];

    setValue('learningModes', updatedModes, {
      shouldValidate: true,
    });
  };

  const onSubmit = (data: PreferencesFormData) => {
    setPreferences({
      language: data.language,
      learningModes: data.learningModes,
    });

    setCurrentStep(5);
    router.push('/onboarding/profile');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Step 4 of 6
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Set your learning preferences
          </h1>

          <p className="mt-2 text-[var(--text-secondary)]">
            Tell UniOS how you prefer to learn.
          </p>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-8"
        >
          {/* Language */}
          <section>
            <label className="mb-4 block text-sm font-semibold text-[var(--text-label)]">
              Preferred Learning Language
            </label>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
              {languages.map((language) => {
                const selected =
                  selectedLanguage === language.value;

                return (
                  <button
                    key={language.value}
                    type="button"
                    onClick={() =>
                      selectLanguage(language.value)
                    }
                    className={`rounded-xl border px-4 py-3 text-sm font-medium transition ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                        : 'border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)] hover:border-[var(--primary)]'
                    }`}
                  >
                    {language.label}
                  </button>
                );
              })}
            </div>

            {errors.language && (
              <p className="mt-2 text-sm text-[var(--danger)]">
                {errors.language.message}
              </p>
            )}
          </section>

          {/* Learning Modes */}
          <section>
            <label className="mb-4 block text-sm font-semibold text-[var(--text-label)]">
              How do you prefer to learn?
            </label>

            <p className="mb-4 text-sm text-[var(--text-secondary)]">
              Select one or more learning modes.
            </p>

            <div className="grid gap-3 sm:grid-cols-2">
              {learningModes.map((mode) => {
                const selected =
                  selectedModes?.includes(mode.value);

                return (
                  <button
                    key={mode.value}
                    type="button"
                    onClick={() =>
                      toggleLearningMode(mode.value)
                    }
                    className={`rounded-xl border p-5 text-left transition ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)]'
                        : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--primary)]'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border ${
                          selected
                            ? 'border-[var(--primary)] bg-[var(--primary)] text-white'
                            : 'border-[var(--border)]'
                        }`}
                      >
                        {selected && (
                          <span className="text-xs">✓</span>
                        )}
                      </div>

                      <div>
                        <p className="font-semibold text-[var(--text-primary)]">
                          {mode.label}
                        </p>

                        <p className="mt-1 text-sm leading-5 text-[var(--text-secondary)]">
                          {mode.description}
                        </p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {errors.learningModes && (
              <p className="mt-2 text-sm text-[var(--danger)]">
                {errors.learningModes.message}
              </p>
            )}
          </section>

          {/* Navigation */}
          <div className="flex items-center justify-between border-t border-[var(--border)] pt-6">
            <button
              type="button"
              onClick={() =>
                router.push('/onboarding/skills')
              }
              className="text-sm font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            >
              ← Back to skills
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

