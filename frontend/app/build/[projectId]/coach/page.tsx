
'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';

import BuildCoach from '@/components/build/coach/BuildCoach';

export default function BuildCoachPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params?.projectId;

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

  return <BuildCoach projectId={projectId} />;
}
