'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import {
  educationSchema,
  type EducationFormData,
} from '@/app/validations/onboarding';

import { useOnboardingStore } from '@/stores/onboardingstore';

const academicStatuses = [
  {
    value: 'BACHELOR' as const,
    label: "Bachelor's",
    description: 'Currently pursuing an undergraduate degree',
  },
  {
    value: 'MASTER' as const,
    label: "Master's",
    description: 'Currently pursuing a postgraduate degree',
  },
  {
    value: 'RECENT_GRADUATE' as const,
    label: 'Recent Graduate',
    description: 'Recently completed your degree',
  },
];

const bachelorYears = [
  'Year 1',
  'Year 2',
  'Year 3',
  'Year 4',
  'Year 5',
];

const masterYears = [
  'Year 1',
  'Year 2',
];

const graduationYears = [
  '2022',
  '2023',
  '2024',
  '2025',
  '2026',
];

export default function EducationOnboarding() {
  const router = useRouter();

  const {
    education,
    setEducation,
    setCurrentStep,
  } = useOnboardingStore();

  const [subjectsInput, setSubjectsInput] = useState(
    education.subjects?.join(', ') || ''
  );

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<EducationFormData>({
    resolver: zodResolver(educationSchema),
    defaultValues: {
      academicStatus: education.academicStatus || undefined,
      university: education.university || '',
      degreeProgram: education.degreeProgram || '',
      domain: education.domain || '',
      currentYear: education.currentYear || '',
      subjects: education.subjects || [],
      graduationYear: education.graduationYear || '',
      degree: education.degree || '',
    },
  });

  const academicStatus = watch('academicStatus');

  const handleAcademicStatusChange = (
    status: EducationFormData['academicStatus']
  ) => {
    setValue('academicStatus', status, {
      shouldValidate: true,
      shouldDirty: true,
    });
  };

  const onSubmit = (data: EducationFormData) => {
  const subjects = subjectsInput
    .split(',')
    .map((subject) => subject.trim())
    .filter(Boolean);

  const isStudent =
    data.academicStatus === 'BACHELOR' ||
    data.academicStatus === 'MASTER';

  // Keep RHF state synchronized with the actual textarea value
  setValue('subjects', subjects, {
    shouldValidate: true,
    shouldDirty: true,
  });

  setEducation({
    academicStatus: data.academicStatus,

    university: isStudent
      ? data.university
      : '',

    degreeProgram: isStudent
      ? data.degreeProgram
      : '',

    domain: data.domain,

    currentYear: isStudent
      ? data.currentYear
      : '',

    subjects: isStudent
      ? subjects
      : [],

    graduationYear:
      data.academicStatus === 'RECENT_GRADUATE'
        ? data.graduationYear
        : '',

    degree:
      data.academicStatus === 'RECENT_GRADUATE'
        ? data.degree
        : '',
  });

  setCurrentStep(2);
  router.push('/onboarding/career');
};
  const currentYearOptions =
    academicStatus === 'MASTER'
      ? masterYears
      : bachelorYears;

  return (
    <div className="min-h-screen bg-[var(--surface)] flex flex-col font-inter">
      <main className="flex-grow flex items-center justify-center p-4 sm:p-8 lg:p-12">
        <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-[1fr_0.8fr] gap-12 lg:gap-20 items-start">

          {/* LEFT CONTENT */}
          <div className="flex flex-col justify-center pt-4 lg:pt-8 max-w-xl">

            <div className="mb-8">
              <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
                Step 1 of 6
              </p>

              <h1 className="text-3xl sm:text-4xl font-bold text-[var(--text-primary)] mb-3 tracking-tight">
                Tell us about your education
              </h1>

              <p className="text-sm sm:text-base text-[var(--text-secondary)] leading-relaxed">
                This helps UniOS understand your academic background and
                personalize your learning journey.
              </p>
            </div>

            <form
              onSubmit={handleSubmit(onSubmit)}
              className="space-y-6"
            >

              {/* ACADEMIC STATUS */}
              <div>
                <label className="block text-sm font-semibold text-[var(--text-label)] mb-3">
                  What is your current academic status?
                </label>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {academicStatuses.map((status) => {
                    const selected =
                      academicStatus === status.value;

                    return (
                      <button
                        key={status.value}
                        type="button"
                        onClick={() =>
                          handleAcademicStatusChange(status.value)
                        }
                        className={`text-left p-4 rounded-xl border transition-all duration-200 ${
                          selected
                            ? 'border-[var(--primary)] bg-[var(--primary-soft)] shadow-sm ring-1 ring-[var(--primary)]'
                            : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--primary)] hover:bg-[var(--surface-alt)]'
                        }`}
                      >
                        <div
                          className={`text-sm font-bold mb-1 ${
                            selected
                              ? 'text-[var(--primary)]'
                              : 'text-[var(--text-primary)]'
                          }`}
                        >
                          {status.label}
                        </div>

                        <div className="text-[11px] text-[var(--text-secondary)] leading-snug">
                          {status.description}
                        </div>
                      </button>
                    );
                  })}
                </div>

                {errors.academicStatus && (
                  <p className="mt-2 text-xs font-medium text-[var(--danger)]">
                    {errors.academicStatus.message}
                  </p>
                )}
              </div>

              {/* BACHELOR / MASTER */}
              {(academicStatus === 'BACHELOR' ||
                academicStatus === 'MASTER') && (
                <div className="space-y-5">

                  {/* UNIVERSITY */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      University Name
                    </label>

                    <input
                      type="text"
                      {...register('university')}
                      placeholder="e.g. Central University of Punjab"
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                    />

                    {errors.university && (
                      <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">
                        {errors.university.message}
                      </p>
                    )}
                  </div>

                  {/* DEGREE PROGRAM */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      Degree Program
                    </label>

                    <input
                      type="text"
                      {...register('degreeProgram')}
                      placeholder="e.g. B.Tech Computer Science and Engineering"
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                    />

                    {errors.degreeProgram && (
                      <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">
                        {errors.degreeProgram.message}
                      </p>
                    )}
                  </div>

                  {/* DOMAIN + CURRENT YEAR */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">

                    {/* DOMAIN */}
                    <div>
                      <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                        Domain
                      </label>

                      <input
                        type="text"
                        {...register('domain')}
                        placeholder="e.g. Computer Science"
                        className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                      />

                      {errors.domain && (
                        <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">
                          {errors.domain.message}
                        </p>
                      )}
                    </div>

                    {/* CURRENT YEAR */}
                    <div>
                      <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                        Current Year
                      </label>

                      <select
                        {...register('currentYear')}
                        className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm appearance-none cursor-pointer"
                      >
                        <option value="" disabled>
                          Select year
                        </option>

                        {currentYearOptions.map((year) => (
                          <option
                            key={year}
                            value={year}
                          >
                            {year}
                          </option>
                        ))}
                      </select>

                      {errors.currentYear && (
                        <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">
                          {errors.currentYear.message}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* SUBJECTS */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      Subjects
                    </label>

                    <textarea
  value={subjectsInput}
  onChange={(event) => {
    const value = event.target.value;

    setSubjectsInput(value);

    const subjects = value
      .split(',')
      .map((subject) => subject.trim())
      .filter(Boolean);

    setValue('subjects', subjects, {
      shouldValidate: true,
      shouldDirty: true,
    });
  }}
  rows={3}
  placeholder="e.g. DBMS, Operating Systems, Computer Networks"
  className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] resize-none focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
/>

{errors.subjects && (
  <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">
    {errors.subjects.message}
  </p>)}

<p className="mt-1.5 text-xs text-[var(--text-muted)]">
  Separate multiple subjects with commas.
</p>
                  </div>
                </div>
              )}

              {/* RECENT GRADUATE */}
              {academicStatus === 'RECENT_GRADUATE' && (
                <div className="space-y-5">

                  {/* GRADUATION YEAR */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      Graduation Year
                    </label>

                    <select
                      {...register('graduationYear')}
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm appearance-none cursor-pointer"
                    >
                      <option value="" disabled>
                        Select graduation year
                      </option>

                      {graduationYears.map((year) => (
                        <option
                          key={year}
                          value={year}
                        >
                          {year}
                        </option>
                      ))}
                    </select>

                    {errors.graduationYear && (
                      <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">
                        {errors.graduationYear.message}
                      </p>
                    )}
                  </div>

                  {/* DEGREE */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      Degree
                    </label>

                    <input
                      type="text"
                      {...register('degree')}
                      placeholder="e.g. B.Tech Computer Science"
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                    />

                    {errors.degree && (
                      <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">
                        {errors.degree.message}
                      </p>
                    )}
                  </div>

                  {/* DOMAIN */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      Domain
                    </label>

                    <input
                      type="text"
                      {...register('domain')}
                      placeholder="e.g. Computer Science"
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                    />

                    {errors.domain && (
                      <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">
                        {errors.domain.message}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* CONTINUE */}
              <div className="pt-8 mt-8 border-t border-[var(--border)]">
                <button
                  type="submit"
                  className="w-full sm:w-auto px-10 py-3.5 bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white text-sm font-bold rounded-xl transition-all shadow-[0_4px_14px_0_var(--primary-shadow)] hover:shadow-lg hover:-translate-y-0.5"
                >
                  Continue to Next Step
                </button>
              </div>
            </form>
          </div>

          {/* RIGHT PANEL */}
          <div className="hidden lg:flex flex-col items-center justify-center bg-[var(--surface-alt)] rounded-[32px] p-12 h-full text-center border border-[var(--border)] sticky top-32">

            <div className="w-[240px] h-[240px] rounded-[32px] overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.1)] mb-10">
              <img
                src="https://images.unsplash.com/photo-1541339907198-e08756dedf3f?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80"
                alt="University Campus"
                className="w-full h-full object-cover"
              />
            </div>

            <h3 className="text-2xl font-bold text-[var(--text-primary)] mb-4 tracking-tight">
              Your academic launchpad
            </h3>

            <p className="text-base text-[var(--text-secondary)] leading-relaxed max-w-xs">
              UniOS uses your academic background to personalize your learning journey.
            </p>

            <div className="flex gap-2 mt-8">
              <div className="w-2 h-2 rounded-full bg-[var(--primary)]" />
              <div className="w-2 h-2 rounded-full bg-[var(--border)]" />
              <div className="w-2 h-2 rounded-full bg-[var(--border)]" />
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}