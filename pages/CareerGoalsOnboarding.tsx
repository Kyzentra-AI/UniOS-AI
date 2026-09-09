'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import {
  careerGoalsSchema,
  type CareerGoalsFormData,
} from '@/app/validations/onboarding';

import { useOnboardingStore } from '@/stores/onboardingstore';

const goalOptions = [
  'Get an Internship',
  'Get a Full-Time Job',
  'Prepare for Placements',
  'Build Projects',
  'Switch Career',
  'Prepare for Higher Studies',
];

const roleOptions = [
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'Software Engineer',
  'Data Scientist',
  'AI / ML Engineer',
  'DevOps Engineer',
  'Product Manager',
];

const industryOptions = [
  'Technology',
  'FinTech',
  'Healthcare',
  'EdTech',
  'E-commerce',
  'SaaS',
  'AI / Machine Learning',
  'Cybersecurity',
];

export default function CareerGoalsOnboarding() {
  const router = useRouter();

  const {
    careerGoals,
    setCareerGoals,
    setCurrentStep,
  } = useOnboardingStore();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<CareerGoalsFormData>({
    resolver: zodResolver(careerGoalsSchema),
    defaultValues: {
      primaryGoal: careerGoals.primaryGoal,
      targetRoles: careerGoals.targetRoles,
      industries: careerGoals.industries,
    },
  });

  const selectedRoles = watch('targetRoles') || [];
  const selectedIndustries = watch('industries') || [];

  useEffect(() => {
    setCurrentStep(2);
  }, [setCurrentStep]);

  const toggleValue = (
    field: 'targetRoles' | 'industries',
    value: string,
  ) => {
    const current =
      field === 'targetRoles' ? selectedRoles : selectedIndustries;

    if (current.includes(value)) {
      setValue(
        field,
        current.filter((item) => item !== value),
        { shouldValidate: true },
      );
    } else {
      setValue(field, [...current, value], {
        shouldValidate: true,
      });
    }
  };

  const onSubmit = (data: CareerGoalsFormData) => {
    setCareerGoals({
      primaryGoal: data.primaryGoal,
      targetRoles: data.targetRoles,
      industries: data.industries,
    });

    setCurrentStep(3);
    router.push('/onboarding/skills');
  };

  return (
    <div className="min-h-[calc(100vh-64px)] bg-[var(--background)]">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Step 2 of 6
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)] sm:text-4xl">
            What are your career goals?
          </h1>

          <p className="mt-3 max-w-2xl text-[var(--text-secondary)]">
            Tell us where you want to go so UniOS can personalize your
            learning and career journey.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Primary Goal */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              What is your primary goal?
            </h2>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Choose the one goal that matters most to you right now.
            </p>

            <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {goalOptions.map((goal) => {
                const selected = watch('primaryGoal') === goal;

                return (
                  <label
                    key={goal}
                    className={`cursor-pointer rounded-xl border p-4 transition-all ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)]'
                        : 'border-[var(--border)] hover:border-[var(--primary)]'
                    }`}
                  >
                    <input
                      type="radio"
                      value={goal}
                      {...register('primaryGoal')}
                      className="sr-only"
                    />

                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-5 w-5 items-center justify-center rounded-full border ${
                          selected
                            ? 'border-[var(--primary)]'
                            : 'border-[var(--border)]'
                        }`}
                      >
                        {selected && (
                          <div className="h-2.5 w-2.5 rounded-full bg-[var(--primary)]" />
                        )}
                      </div>

                      <span className="text-sm font-medium text-[var(--text-primary)]">
                        {goal}
                      </span>
                    </div>
                  </label>
                );
              })}
            </div>

            {errors.primaryGoal && (
              <p className="mt-3 text-sm text-[var(--danger)]">
                {errors.primaryGoal.message}
              </p>
            )}
          </section>

          {/* Target Roles */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              Which roles are you targeting?
            </h2>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Select all roles you are interested in.
            </p>

            <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {roleOptions.map((role) => {
                const selected = selectedRoles.includes(role);

                return (
                  <label
                    key={role}
                    className={`cursor-pointer rounded-xl border p-4 transition-all ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)]'
                        : 'border-[var(--border)] hover:border-[var(--primary)]'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() =>
                        toggleValue('targetRoles', role)
                      }
                      className="sr-only"
                    />

                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-5 w-5 items-center justify-center rounded-md border ${
                          selected
                            ? 'border-[var(--primary)] bg-[var(--primary)] text-white'
                            : 'border-[var(--border)]'
                        }`}
                      >
                        {selected && '✓'}
                      </div>

                      <span className="text-sm font-medium text-[var(--text-primary)]">
                        {role}
                      </span>
                    </div>
                  </label>
                );
              })}
            </div>

            {errors.targetRoles && (
              <p className="mt-3 text-sm text-[var(--danger)]">
                {errors.targetRoles.message}
              </p>
            )}
          </section>

          {/* Industries */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              Which industries interest you?
            </h2>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Select the industries you would like to explore.
            </p>

            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {industryOptions.map((industry) => {
                const selected = selectedIndustries.includes(industry);

                return (
                  <label
                    key={industry}
                    className={`cursor-pointer rounded-xl border p-4 text-center transition-all ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)]'
                        : 'border-[var(--border)] hover:border-[var(--primary)]'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() =>
                        toggleValue('industries', industry)
                      }
                      className="sr-only"
                    />

                    <span
                      className={`text-sm font-medium ${
                        selected
                          ? 'text-[var(--primary)]'
                          : 'text-[var(--text-primary)]'
                      }`}
                    >
                      {industry}
                    </span>
                  </label>
                );
              })}
            </div>

            {errors.industries && (
              <p className="mt-3 text-sm text-[var(--danger)]">
                {errors.industries.message}
              </p>
            )}
          </section>

          {/* Actions */}
          <div className="flex items-center justify-between border-t border-[var(--border)] pt-6">
            <button
              type="button"
              onClick={() => router.push('/onboarding/education')}
              className="rounded-xl border border-[var(--border)] px-5 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition-colors hover:border-[var(--primary)]"
            >
              Back
            </button>

            <button
              type="submit"
              className="rounded-xl bg-[var(--primary)] px-6 py-2.5 text-sm font-semibold text-white shadow-[0_4px_14px_0_var(--primary-shadow)] transition-all hover:bg-[var(--primary-hover)] hover:-translate-y-0.5"
            >
              Continue
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}