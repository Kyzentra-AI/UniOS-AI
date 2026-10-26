
'use client';

import Link from 'next/link';

import { useResumes } from '@/hooks/useLaunch';
import {
  LaunchErrorState,
  LaunchLoadingState,
  LaunchEmptyState,
} from '@/components/launch/states/LaunchStates';

export default function LaunchWorkspace() {
  const resumes = useResumes();

  return (
    <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm font-medium text-[var(--feature-blue)]">
          LAUNCH SPRINT
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[var(--text-primary)]">
          Your career workspace
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
          Build a professional resume, review your saved drafts and
          check your resume against implemented ATS criteria.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
        
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">
            AI Resume Builder
          </h2>
          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            Create a resume from your existing profile or enter
            your details manually. Review generated content before saving.
          </p>
          <Link
            href="/launch/resume"
            className="mt-6 inline-flex rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-medium text-white transition hover:bg-[var(--primary-hover)]"
          >
            Open Resume Builder
          </Link>
        </section>

        <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
          
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">
            ATS Resume Checker
          </h2>
          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            Upload a supported resume to inspect actual findings,
            recommendations and a documented score when available.
          </p>
          <Link
            href="/launch/ats"
            className="mt-6 inline-flex rounded-xl border border-[var(--border)] px-5 py-3 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--primary-soft)]"
          >
            Check Resume
          </Link>
        </section>
      </div>

      <section className="mt-10">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold text-[var(--text-primary)]">
              Your saved resumes
            </h2>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Resumes saved to your account.
            </p>
          </div>
          <Link
            href="/launch/resume/new"
            className="rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
          >
            + New resume
          </Link>
        </div>

        {resumes.isPending ? (
          <LaunchLoadingState message="Loading your saved resumes..." />
        ) : resumes.isError ? (
          <LaunchErrorState
            message={resumes.error.message}
            action={
              <button
                onClick={() => void resumes.refetch()}
                className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm text-white"
              >
                Try again
              </button>
            }
          />
        ) : resumes.data.items.length === 0 ? (
          <LaunchEmptyState
            title="No resumes saved yet"
            message="Start with your profile or create a resume manually."
            action={
              <Link
                href="/launch/resume/new"
                className="rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm text-white"
              >
                Create your first resume
              </Link>
            }
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {resumes.data.items.map((resume) => (
              <Link
                key={resume.id}
                href={`/launch/resume/${encodeURIComponent(resume.id)}`}
                className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 transition hover:border-[var(--primary)]"
              >
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-semibold text-[var(--text-primary)]">
                    {resume.title}
                  </h3>
                  <span className="rounded-full bg-[var(--primary-soft)] px-2.5 py-1 text-xs text-[var(--primary)]">
                    {resume.status}
                  </span>
                </div>
                <p className="mt-3 text-sm text-[var(--text-secondary)]">
                  {resume.source === 'profile'
                    ? 'Profile-based'
                    : 'Manual'}
                </p>
                <p className="mt-4 text-xs text-[var(--text-muted)]">
                  Updated{' '}
                  {new Date(resume.updatedAt).toLocaleDateString()}
                </p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
