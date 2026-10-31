'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';

import BuildArtifacts from '@/components/build/artifacts/BuildArtifacts';
import { BuildEmpty } from '@/components/build/states/BuildStates';

export default function BuildArtifactsPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params?.projectId;

  if (!projectId) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-8">
        <BuildEmpty
          title="Invalid project URL"
          description="Invalid project URL. Please return to Build and select a project."
          action={
            <Link
              href="/build"
              className="rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
            >
              Back to Build
            </Link>
          }
        />
      </main>
    );
  }

  return <BuildArtifacts projectId={projectId} />;
}