
'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';

import { useBuild } from '@/hooks/useBuild';
import BuildWorkspace from '@/components/build/workspace/BuildWorkspace';
import {
  BuildError,
  BuildLoading,
} from '@/components/build/states/BuildStates';

export default function ProjectBuildPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params?.projectId ?? '';

  const {
    getProject,
    loading,
    hydrated,
    error,
    refresh,
  } = useBuild(projectId);

  const project = projectId ? getProject(projectId) : undefined;

  if (!projectId) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-8">
        <p className="text-sm text-[var(--muted-foreground)]">
          Invalid project URL. Please return to Build and select a project.
        </p>

        <Link
          href="/build"
          className="mt-4 inline-block text-sm font-medium text-[var(--primary)]"
        >
          Back to Build
        </Link>
      </main>
    );
  }

  if (loading && !hydrated) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-8">
        <BuildLoading label="Opening project…" />
      </main>
    );
  }

  if (!project) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-8">
        <BuildError
          message={error ?? 'Project not found.'}
          onRetry={() => void refresh()}
        />

        <Link
          href="/build"
          className="mt-4 inline-block text-sm font-medium text-[var(--primary)]"
        >
          Back to Build
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6">
        <Link
          href="/build"
          className="text-sm font-medium text-[var(--primary)]"
        >
          ← All projects
        </Link>

        <div className="mt-4 flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--primary)]">
              Project workspace
            </p>

            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[var(--foreground)]">
              {project.title}
            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--muted-foreground)]">
              {project.description ||
                'Use this workspace to plan the work, track milestones, and record evidence of what you build.'}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link
              href={`/build/${projectId}/artifacts`}
              className="rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm font-semibold text-[var(--foreground)]"
            >
              Artifacts
            </Link>

            <Link
              href={`/build/${projectId}/coach`}
              className="rounded-xl bg-[var(--primary)] px-3.5 py-2.5 text-sm font-semibold text-white"
            >
              Project Coach
            </Link>
          </div>
        </div>
      </div>

      <BuildWorkspace project={project} />
    </main>
  );
}
