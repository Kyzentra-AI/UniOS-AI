'use client';

import { use } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import MissionCard from '@/components/roadmap/MissionCard';
import { Chevron } from '@/components/roadmap/UI';
import { useMission } from '@/hooks/useMission';

interface MissionsPageProps {
  params: Promise<{
    id: string;
  }>;
}

function BackLink() {
  return (
    <Link
      href="/roadmap"
      className="group inline-flex items-center gap-1 rounded-md py-1 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
      style={{ color: 'var(--primary)' }}
    >
      <Chevron className="rotate-180 transition-transform duration-200 group-hover:-translate-x-0.5" />
      Back to roadmap
    </Link>
  );
}

export default function MissionsPage({
  params,
}: MissionsPageProps) {
  const { id } = use(params);
  const router = useRouter();

  const {
    mission,
    isLoading,
    error,
    startMission,
    completeMission,
    deferMission,
    skipMission,
    isStarting,
    isCompleting,
    isDeferring,
    isSkipping,
  } = useMission(id);

  const handleStart = async () => {
    if (!mission) return;

    try {
      await startMission(mission.id);

      const searchParams = new URLSearchParams({
        topic: mission.subject || mission.title,
        lesson_id: mission.id,
        mission_id: mission.id,
      });

      if (mission.roadmap_id) {
        searchParams.set('roadmap_id', mission.roadmap_id);
      }

      router.push(`/learning?${searchParams.toString()}`);
    } catch (error) {
      
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen px-4 py-6 sm:px-6 sm:py-10">
        <div role="status" aria-live="polite" className="mx-auto max-w-3xl">
          <BackLink />
          <span className="sr-only">Loading mission...</span>

          <div
            className="rise mt-5 overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_28px_rgba(24,52,58,0.04)]"
            aria-hidden="true"
          >
            <div className="space-y-4 p-5 sm:p-8">
              <div className="flex flex-wrap gap-2">
                <div className="skeleton h-6 w-20 rounded-full" />
                <div className="skeleton h-6 w-28 rounded-full" />
                <div className="skeleton h-6 w-16 rounded-full" />
              </div>

              <div className="skeleton h-8 w-4/5 rounded-lg" />

              <div className="space-y-2.5 pt-1">
                <div className="skeleton h-4 w-full rounded-md" />
                <div className="skeleton h-4 w-11/12 rounded-md" />
                <div className="skeleton h-4 w-2/3 rounded-md" />
              </div>
            </div>

            <div className="grid grid-cols-3 divide-x divide-[var(--border)] border-t border-[var(--border)]">
              {[0, 1, 2].map((n) => (
                <div key={n} className="space-y-2 p-4 sm:p-5">
                  <div className="skeleton h-3 w-12 rounded-md" />
                  <div className="skeleton h-5 w-16 rounded-md" />
                </div>
              ))}
            </div>

            <div className="flex flex-col gap-2 border-t border-[var(--border)] bg-[var(--surface-alt)] p-5 sm:flex-row sm:p-6">
              <div className="skeleton h-11 w-full rounded-xl sm:w-36" />
              <div className="skeleton h-11 w-full rounded-xl sm:w-28" />
              <div className="skeleton h-11 w-full rounded-xl sm:w-28" />
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (error || !mission) {
    return (
      <main className="min-h-screen px-4 py-6 sm:px-6 sm:py-10">
        <div className="mx-auto max-w-3xl">
          <BackLink />

          <div
            role="alert"
            className="rise mt-5 rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-8"
          >
            <div className="flex items-center gap-2.5">
              <span
                className="h-2 w-2 shrink-0 rounded-full"
                style={{ backgroundColor: 'var(--danger)' }}
              />
              <h1
                className="text-lg font-semibold"
                style={{ color: 'var(--text-primary)' }}
              >
                Failed to load mission.
              </h1>
            </div>

            {error && (
              <p
                className="mt-2 break-words pl-[18px] text-sm leading-6"
                style={{ color: 'var(--text-secondary)' }}
              >
                {error instanceof Error
                  ? error.message
                  : 'An unexpected error occurred.'}
              </p>
            )}

            <button
              type="button"
              onClick={() => router.push('/roadmap')}
              className="ml-[18px] mt-5 rounded-xl border px-4 py-2.5 text-sm font-semibold transition hover:border-[var(--primary)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
              style={{
                borderColor: 'var(--border)',
                color: 'var(--text-primary)',
              }}
            >
              Back to roadmap
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-4 py-6 sm:px-6 sm:py-10">
      <div className="mx-auto max-w-3xl">
        <BackLink />

        <div className="rise mt-5">
          <MissionCard
            mission={mission}
            onStart={handleStart}
            onComplete={() => completeMission(mission.id)}
            onDefer={() => deferMission(mission.id)}
            onSkip={() => skipMission(mission.id)}
            isStarting={isStarting}
            isCompleting={isCompleting}
            isDeferring={isDeferring}
            isSkipping={isSkipping}
          />
        </div>
      </div>
    </main>
  );
}