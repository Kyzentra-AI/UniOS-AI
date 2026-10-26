'use client';

import Link from 'next/link';

import MissionCard from '@/components/roadmap/MissionCard';
import { Chevron } from '@/components/roadmap/UI';
import { useMission } from '@/hooks/useMission';

interface MissionsPageProps {
  params: {
    id: string;
  };
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
  } = useMission(params.id);

  if (isLoading) {
    return (
      <main className="min-h-screen px-4 py-6 sm:px-6 sm:py-10">
        <div
          role="status"
          aria-live="polite"
          className="mx-auto max-w-3xl"
        >
          <BackLink />

          <div className="rise mt-5 rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-8">
            <div className="flex items-center gap-3 text-sm text-[var(--text-secondary)]">
              <span className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
              Loading mission...
            </div>

            <div className="mt-6 space-y-4" aria-hidden="true">
              <div className="flex gap-2">
                <div className="skeleton h-6 w-20 rounded-full" />
                <div className="skeleton h-6 w-28 rounded-full" />
              </div>
              <div className="skeleton h-7 w-3/4 rounded-md" />
              <div className="skeleton h-4 w-full rounded-md" />
              <div className="skeleton h-4 w-5/6 rounded-md" />
              <div className="flex gap-2 pt-3">
                <div className="skeleton h-11 w-32 rounded-xl" />
                <div className="skeleton h-11 w-24 rounded-xl" />
              </div>
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

            <p
              className="mt-2 pl-[18px] text-sm leading-6"
              style={{ color: 'var(--text-secondary)' }}
            >
              This mission may have been removed, or something went wrong
              while loading it. Head back to your roadmap and try opening it again.
            </p>

            <Link
              href="/roadmap"
              className="ml-[18px] mt-5 inline-flex rounded-xl px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
              style={{ backgroundColor: 'var(--primary)' }}
            >
              View roadmap
            </Link>
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
            onStart={() => startMission(mission.id)}
            onComplete={() =>
              completeMission(mission.id)
            }
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