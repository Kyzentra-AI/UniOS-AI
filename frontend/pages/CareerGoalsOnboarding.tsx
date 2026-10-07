
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import {
  careerGoalsSchema,
  type CareerGoalsFormData,
} from '@/app/validations/onboarding';

import { useOnboardingStore } from '@/stores/onboardingstore';

export default function CareerGoalsOnboarding() {
  const router = useRouter();

  const {
    careerGoals,
    setCareerGoals,
    setCurrentStep,
  } = useOnboardingStore();

  const [skillInput, setSkillInput] = useState(
    ''
  );

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CareerGoalsFormData>({
    resolver: zodResolver(careerGoalsSchema),
    defaultValues: {
      primaryGoal: careerGoals.primaryGoal,
      targetSkills: careerGoals.targetSkills,
    },
  });

  const targetSkills = watch('targetSkills') || [];

  useEffect(() => {
    setCurrentStep(2);
  }, [setCurrentStep]);

  const addSkill = () => {
    const skill = skillInput.trim();

    if (!skill) return;

    if (
      targetSkills.some(
        (existingSkill) =>
          existingSkill.toLowerCase() === skill.toLowerCase()
      )
    ) {
      setSkillInput('');
      return;
    }

    setValue(
      'targetSkills',
      [...targetSkills, skill],
      {
        shouldValidate: true,
        shouldDirty: true,
      }
    );

    setSkillInput('');
  };

  const removeSkill = (skillToRemove: string) => {
    setValue(
      'targetSkills',
      targetSkills.filter(
        (skill) => skill !== skillToRemove
      ),
      {
        shouldValidate: true,
        shouldDirty: true,
      }
    );
  };

  const handleSkillKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      addSkill();
    }
  };

  const onSubmit = (data: CareerGoalsFormData) => {
    setCareerGoals({
      primaryGoal: data.primaryGoal,
      targetSkills: data.targetSkills,
    });

    setCurrentStep(3);
    router.push('/onboarding/skills');
  };

  return (
    <div className="min-h-[calc(100vh-64px)] bg-[var(--background)]">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">

        {/* HEADER */}
        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Step 2 of 6
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)] sm:text-4xl">
            What are your career goals?
          </h1>

          <p className="mt-3 max-w-2xl text-[var(--text-secondary)]">
            Tell us where you want to go and what skills you want to
            develop so UniOS can personalize your learning journey.
          </p>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-8"
        >

          {/* PRIMARY GOAL */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">

            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              What is your primary goal?
            </h2>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Describe what you want to achieve in your own words.
            </p>

            <div className="mt-5">
              <textarea
                {...register('primaryGoal')}
                rows={5}
                placeholder="e.g. I want to become a full-stack AI developer and eventually work on intelligent learning systems."
                className="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3.5 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] shadow-sm transition-all focus:border-[var(--primary)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)]"
              />

              {errors.primaryGoal && (
                <p className="mt-2 text-sm text-[var(--danger)]">
                  {errors.primaryGoal.message}
                </p>
              )}
            </div>
          </section>

          {/* TARGET SKILLS */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">

            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              What skills do you want to achieve?
            </h2>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Add the skills you want to learn or become proficient in.
            </p>

            {/* ADD SKILL */}
            <div className="mt-5 flex flex-col gap-3 sm:flex-row">

              <input
                type="text"
                value={skillInput}
                onChange={(event) =>
                  setSkillInput(event.target.value)
                }
                onKeyDown={handleSkillKeyDown}
                placeholder="e.g. React, Python, Canva, Communication"
                className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3.5 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] shadow-sm transition-all focus:border-[var(--primary)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)]"
              />

              <button
                type="button"
                onClick={addSkill}
                className="rounded-xl bg-[var(--primary)] px-6 py-3.5 text-sm font-semibold text-white transition-all hover:bg-[var(--primary-hover)]"
              >
                Add Skill
              </button>

            </div>

            {/* SKILL CHIPS */}
            {targetSkills.length > 0 && (
              <div className="mt-5">

                <p className="mb-3 text-sm font-medium text-[var(--text-secondary)]">
                  Your target skills
                </p>

                <div className="flex flex-wrap gap-2">

                  {targetSkills.map((skill) => (
                    <div
                      key={skill}
                      className="flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-alt)] px-3.5 py-2 text-sm text-[var(--text-primary)]"
                    >
                      <span>{skill}</span>

                      <button
                        type="button"
                        onClick={() => removeSkill(skill)}
                        aria-label={`Remove ${skill}`}
                        className="flex h-5 w-5 items-center justify-center rounded-full text-[var(--text-secondary)] transition-colors hover:bg-[var(--danger)] hover:text-white"
                      >
                        ×
                      </button>
                    </div>
                  ))}

                </div>
              </div>
            )}

            {errors.targetSkills && (
              <p className="mt-3 text-sm text-[var(--danger)]">
                {errors.targetSkills.message}
              </p>
            )}

          </section>

          {/* ACTIONS */}
          <div className="flex items-center justify-between border-t border-[var(--border)] pt-6">

            <button
              type="button"
              onClick={() =>
                router.push('/onboarding/education')
              }
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
