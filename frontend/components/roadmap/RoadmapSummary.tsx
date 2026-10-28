'use client';

import Link from 'next/link';

import { useRoadmap } from '@/hooks/useRoadmap';
import { Chevron, Node, ProgressRing, stagger } from './UI';

export default function RoadmapSummary() {
  const {
    roadmap,
    isLoading,
    isError,
  } = useRoadmap();

  if (isLoading) {
    return (
      <section className="space-y-6" aria-busy="true" aria-label="Loading roadmap">
        <div className="space-y-2">
          <div className="skeleton h-6 w-36 rounded-md" />
          <div className="skeleton h-4 w-56 max-w-full rounded-md" />
        </div>

        <div className="flex items-center gap-5 rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
          <div className="skeleton h-24 w-24 shrink-0 rounded-full" />
          <div className="flex-1 space-y-2.5">
            <div className="skeleton h-3 w-12 rounded-md" />
            <div className="skeleton h-5 w-4/5 rounded-md" />
            <div className="skeleton h-3 w-2/3 rounded-md" />
          </div>
        </div>

        <div className="space-y-3 pl-11">
          {[0, 1, 2].map((n) => (
            <div key={n} className="skeleton h-[72px] rounded-2xl" />
          ))}
        </div>
      </section>
    );
  }

  if (isError || !roadmap) {
    return (
      <section className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">
          Your Roadmap
        </h2>

        <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
          {isError
            ? "We couldn’t load your roadmap right now."
            : "Your roadmap hasn’t been generated yet. Upload your syllabus to get started."}
        </p>

        {!isError && (
          <Link
            href="/syllabus"
            className="group mt-5 inline-flex w-full items-center justify-center gap-1 rounded-xl bg-[var(--text-primary)] px-5 py-3 text-sm font-medium text-[var(--background)] transition hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2 sm:w-auto"
          >
            Upload Syllabus
            <Chevron className="transition-transform duration-200 group-hover:translate-x-0.5" />
          </Link>
        )}
      </section>
    );
  }

  const completedMissions =
    roadmap.missions.filter(
      (mission) =>
        mission.status === 'COMPLETED'
    ).length;

  const totalMissions =
    roadmap.missions.length;

  const progress =
    totalMissions > 0
      ? Math.round(
          (completedMissions /
            totalMissions) *
            100
        )
      : 0;

  const currentMission =
    roadmap.missions.find(
      (mission) =>
        mission.status === 'IN_PROGRESS'
    ) ??
    roadmap.missions.find(
      (mission) =>
        mission.status === 'PENDING'
    ) ??
    roadmap.missions.find(
      (mission) =>
        mission.status === 'DEFERRED'
    );

  const visibleMissions =
    [...roadmap.missions]
      .sort((a, b) => {
        if (a.week !== b.week) {
          return a.week - b.week;
        }

        return (
          a.sequence - b.sequence
        );
      })
      .slice(0, 5);

  return (
    <section className="space-y-8">
      {/* Roadmap */}
      <div>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-x-4 gap-y-1">
          <div className="min-w-0">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              Your Roadmap
            </h2>

            <p className="mt-0.5 text-sm text-[var(--text-secondary)]">
              Your current learning direction and progress.
            </p>
          </div>

          <Link
            href="/roadmap"
            className="group inline-flex items-center gap-0.5 rounded-md py-1 text-sm font-medium text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
          >
            View full roadmap
            <Chevron className="transition-transform duration-200 group-hover:translate-x-0.5" />
          </Link>
        </div>

        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-6">
          <div className="flex items-center gap-5">
            <ProgressRing value={progress} size={96} stroke={9} />

            <div className="min-w-0">
              <p className="text-xs text-[var(--text-muted)]">Scope</p>
              <p className="mt-0.5 line-clamp-2 text-lg font-semibold leading-snug text-[var(--text-primary)]">
                {roadmap.scope}
              </p>
              <p className="mt-1.5 text-xs text-[var(--text-secondary)]">
                {completedMissions} of{' '}
                {totalMissions} missions
                completed
              </p>
            </div>
          </div>

          {/* Current Focus */}
          <div className="mt-5 rounded-2xl bg-[var(--surface-alt)] p-4">
            <p className="text-xs text-[var(--text-muted)]">Current focus</p>

            {currentMission ? (
              <Link
                href={`/missions/${currentMission.id}`}
                className="group mt-1 flex items-center justify-between gap-3 rounded-md text-sm font-medium text-[var(--text-primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
              >
                <span className="line-clamp-2 min-w-0">{currentMission.title}</span>
                <Chevron className="shrink-0 text-[var(--text-muted)] transition-transform duration-200 group-hover:translate-x-0.5" />
              </Link>
            ) : (
              <p className="mt-1 text-sm text-[var(--text-primary)]">
                No active mission
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Missions */}
      <div>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-x-4 gap-y-1">
          <div className="min-w-0">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              Missions
            </h2>

            <p className="mt-0.5 text-sm text-[var(--text-secondary)]">
              Your upcoming learning tasks.
            </p>
          </div>

          <Link
            href="/roadmap"
            className="group inline-flex items-center gap-0.5 rounded-md py-1 text-sm font-medium text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
          >
            View all
            <Chevron className="transition-transform duration-200 group-hover:translate-x-0.5" />
          </Link>
        </div>

        {visibleMissions.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-5">
            <p className="text-sm text-[var(--text-secondary)]">
              No missions available yet.
            </p>
          </div>
        ) : (
          <ol className="relative">
            <span
              aria-hidden="true"
              className="line-grow absolute bottom-7 left-[14px] top-7 w-px bg-[var(--border)]"
            />

            {visibleMissions.map((mission, i) => {
              const completed =
                mission.status === 'COMPLETED';

              const inProgress =
                mission.status === 'IN_PROGRESS';

              return (
                <li
                  key={mission.id}
                  className="rise relative pb-2 pl-11 last:pb-0"
                  style={stagger(i)}
                >
                  <span className="absolute left-0 top-3">
                    <Node state={completed ? 'done' : inProgress ? 'active' : 'idle'}>
                      {mission.sequence}
                    </Node>
                  </span>

                  <Link
                    href={`/missions/${mission.id}`}
                    className="group flex items-center gap-3 rounded-2xl px-3 py-3 transition-colors hover:bg-[var(--surface-alt)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                  >
                    <span className="min-w-0 flex-1">
                      <span
                        className={`line-clamp-2 block text-sm font-medium ${
                          completed ? 'text-[var(--text-secondary)]' : 'text-[var(--text-primary)]'
                        }`}
                      >
                        {mission.title}
                      </span>

                      <span className="mt-1 block text-xs text-[var(--text-muted)]">
                        {mission.mission_type}
                        {mission.subject
                          ? ` · ${mission.subject}`
                          : ''}
                        {' · '}
                        {mission.estimated_minutes} min
                        <span className="text-[var(--text-secondary)]">
                          {' · '}
                          {mission.status.replaceAll('_', ' ')}
                        </span>
                      </span>
                    </span>

                    <Chevron className="shrink-0 text-[var(--text-muted)] transition-transform duration-200 group-hover:translate-x-0.5" />
                  </Link>
                </li>
              );
            })}
          </ol>
        )}
      </div>
    </section>
  );
}