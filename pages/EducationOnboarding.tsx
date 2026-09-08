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

// Added Steps array for the Onboarding Header to match Figma
const steps = [
  { id: 1, name: 'Education', status: 'current' },
  { id: 2, name: 'Career Goals', status: 'upcoming' },
  { id: 3, name: 'Skills', status: 'upcoming' },
  { id: 4, name: 'Preferences', status: 'upcoming' },
  { id: 5, name: 'Assessment', status: 'upcoming' },
  { id: 6, name: 'Profile', status: 'upcoming' },
  { id: 7, name: 'First Mission', status: 'upcoming' },
];

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

const semesters = [
  'Semester 1',
  'Semester 2',
  'Semester 3',
  'Semester 4',
  'Semester 5',
  'Semester 6',
  'Semester 7',
  'Semester 8',
];

const graduationStatuses = [
  'Graduated',
  'Awaiting Graduation',
];

const graduationYears = [
  '2024',
  '2025',
  '2026',
  '2027',
  '2028',
];

export default function EducationOnboarding() {
  const router = useRouter();

  const {
    education,
    setEducation,
    setCurrentStep,
  } = useOnboardingStore();

  const [subjectsInput, setSubjectsInput] = useState(
    education.currentSubjects.join(', ')
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
      university: education.university,
      degreeProgram: education.degreeProgram,
      semester: education.semester,
      currentSubjects: education.currentSubjects,
      graduationStatus: education.graduationStatus,
      degreeBackground: education.degreeBackground,
      passoutYear: education.passoutYear,
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

    setEducation({
      academicStatus: data.academicStatus,
      university: data.university,
      degreeProgram: data.degreeProgram,
      semester: data.semester,
      currentSubjects: subjects,
      graduationStatus: data.graduationStatus,
      degreeBackground: data.degreeBackground,
      passoutYear: data.passoutYear,
    });

    setCurrentStep(2);
    router.push('/onboarding/career-goals');
  };

  return (
    <div className="min-h-screen bg-[var(--surface)] flex flex-col font-inter">
      
      

      {/* =====================================================
          MAIN ONBOARDING CONTENT
      ====================================================== */}
      <main className="flex-grow flex items-center justify-center p-4 sm:p-8 lg:p-12">
        <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-[1fr_0.8fr] gap-12 lg:gap-20 items-start">
          
          {/* LEFT COLUMN: FORM */}
          <div className="flex flex-col justify-center pt-4 lg:pt-8 max-w-xl">
            
            <div className="mb-8">
              <h1 className="text-3xl sm:text-4xl font-bold text-[var(--text-primary)] mb-3 tracking-tight">
                Tell us about your education
              </h1>
              <p className="text-sm sm:text-base text-[var(--text-secondary)] leading-relaxed">
                We'll customize your course recommendations and industry pathways based on your academic path.
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              
              {/* ACADEMIC STATUS */}
              <div>
                <label className="block text-sm font-semibold text-[var(--text-label)] mb-3">
                  What is your current academic status?
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {academicStatuses.map((status) => {
                    const selected = academicStatus === status.value;
                    return (
                      <button
                        key={status.value}
                        type="button"
                        onClick={() => handleAcademicStatusChange(status.value)}
                        className={`text-left p-4 rounded-xl border transition-all duration-200 ${
                          selected
                            ? 'border-[var(--primary)] bg-[var(--primary-soft)] shadow-sm ring-1 ring-[var(--primary)]'
                            : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--primary)] hover:bg-[var(--surface-alt)]'
                        }`}
                      >
                        <div className={`text-sm font-bold mb-1 ${selected ? 'text-[var(--primary)]' : 'text-[var(--text-primary)]'}`}>
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
                  <p className="mt-2 text-xs font-medium text-[var(--danger)] flex items-center gap-1">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    {errors.academicStatus.message}
                  </p>
                )}
              </div>

              {/* BACHELOR / MASTER FIELDS */}
              {(academicStatus === 'BACHELOR' || academicStatus === 'MASTER') && (
                <div className="space-y-5 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  
                  {/* UNIVERSITY */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      University Name
                    </label>
                    <input
                      type="text"
                      {...register('university')}
                      placeholder="e.g. Stanford University"
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                    />
                    {errors.university && (
                      <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">{errors.university.message}</p>
                    )}
                  </div>

                  {/* DEGREE */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      Degree Program
                    </label>
                    <input
                      type="text"
                      {...register('degreeProgram')}
                      placeholder="e.g. B.S. Computer Science"
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                    />
                    {errors.degreeProgram && (
                      <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">{errors.degreeProgram.message}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    {/* SEMESTER */}
                    <div>
                      <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                        Current Semester
                      </label>
                      <select
                        {...register('semester')}
                        className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm appearance-none cursor-pointer"
                      >
                        <option value="" disabled>Select semester</option>
                        {semesters.map((semester) => (
                          <option key={semester} value={semester}>{semester}</option>
                        ))}
                      </select>
                      {errors.semester && (
                        <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">{errors.semester.message}</p>
                      )}
                    </div>
                  </div>

                  {/* CURRENT SUBJECTS */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      Current Subjects <span className="text-xs font-normal text-[var(--text-muted)] ml-1">(Comma separated)</span>
                    </label>
                    <textarea
                      value={subjectsInput}
                      onChange={(event) => setSubjectsInput(event.target.value)}
                      rows={3}
                      placeholder="e.g. Data Structures, Operating Systems, Computer Networks"
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] resize-none focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                    />
                  </div>
                </div>
              )}

              {/* RECENT GRADUATE FIELDS */}
              {academicStatus === 'RECENT_GRADUATE' && (
                <div className="space-y-5 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    {/* GRADUATION STATUS */}
                    <div>
                      <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                        Graduation Status
                      </label>
                      <select
                        {...register('graduationStatus')}
                        className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm cursor-pointer appearance-none"
                      >
                        <option value="" disabled>Select status</option>
                        {graduationStatuses.map((status) => (
                          <option key={status} value={status}>{status}</option>
                        ))}
                      </select>
                      {errors.graduationStatus && (
                        <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">{errors.graduationStatus.message}</p>
                      )}
                    </div>

                    {/* GRADUATION YEAR */}
                    <div>
                      <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                        Graduation Year
                      </label>
                      <select
                        {...register('passoutYear')}
                        className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm cursor-pointer appearance-none"
                      >
                        <option value="" disabled>Select year</option>
                        {graduationYears.map((year) => (
                          <option key={year} value={year}>{year}</option>
                        ))}
                      </select>
                      {errors.passoutYear && (
                        <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">{errors.passoutYear.message}</p>
                      )}
                    </div>
                  </div>

                  {/* DEGREE BACKGROUND */}
                  <div>
                    <label className="block text-sm font-semibold text-[var(--text-label)] mb-1.5">
                      Degree Background
                    </label>
                    <input
                      type="text"
                      {...register('degreeBackground')}
                      placeholder="e.g. B.Tech Computer Science"
                      className="w-full px-4 py-3.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-4 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-all shadow-sm"
                    />
                    {errors.degreeBackground && (
                      <p className="mt-1.5 text-xs font-medium text-[var(--danger)]">{errors.degreeBackground.message}</p>
                    )}
                  </div>
                </div>
              )}

              {/* CONTINUE BUTTON */}
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

          {/* RIGHT COLUMN: VISUAL INFO CARD (Exact Figma Match) */}
          <div className="hidden lg:flex flex-col items-center justify-center bg-[var(--surface-alt)] rounded-[32px] p-12 h-full text-center border border-[var(--border)] sticky top-32">
            <div className="w-[240px] h-[240px] rounded-[32px] overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.1)] mb-10 transform hover:scale-105 transition-transform duration-500">
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
              UniOS aligns with your university curriculum to reinforce core theories with high-growth engineering skills.
            </p>
            
            {/* Small decorative dots */}
            <div className="flex gap-2 mt-8">
              <div className="w-2 h-2 rounded-full bg-[var(--primary)]"></div>
              <div className="w-2 h-2 rounded-full bg-[var(--border)]"></div>
              <div className="w-2 h-2 rounded-full bg-[var(--border)]"></div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}