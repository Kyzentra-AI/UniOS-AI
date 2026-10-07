
'use client';

import Link from 'next/link';

import { useRoadmap } from '@/hooks/useRoadmap';

export default function RoadmapSummary() {
  const {
    roadmap,
    isLoading,
    isError,
  } = useRoadmap();

  if (isLoading) {
    return (
      <section className="space-y-6">
        <div className="h-7 w-40 animate-pulse rounded-md bg-black/10" />
        <div className="h-48 animate-pulse rounded-2xl bg-black/10" />
      </section>
    );
  }

  if (isError || !roadmap) {
    return (
      <section
        className="rounded-2xl border p-6"
        style={{
          backgroundColor: 'var(--surface)',
          borderColor: 'var(--border)',
        }}
      >
        <h2
          className="text-xl font-semibold"
          style={{
            color: 'var(--text-primary)',
          }}
        >
          Your Roadmap
        </h2>

        <p
          className="mt-2 text-sm"
          style={{
            color: 'var(--text-secondary)',
          }}
        >
          Your roadmap is not available yet.
        </p>

        <Link
          href="/roadmap"
          className="mt-4 inline-block text-sm font-medium"
          style={{
            color: 'var(--primary)',
          }}
        >
          Open roadmap →
        </Link>
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
    <section className="space-y-6">
      {/* Roadmap Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2
            className="text-xl font-semibold"
            style={{
              color: 'var(--text-primary)',
            }}
          >
            Your Roadmap
          </h2>

          <p
            className="mt-1 text-sm"
            style={{
              color: 'var(--text-secondary)',
            }}
          >
            Your current learning direction
            and progress.
          </p>
        </div>

        <Link
          href="/roadmap"
          className="text-sm font-medium"
          style={{
            color: 'var(--primary)',
          }}
        >
          View full roadmap →
        </Link>
      </div>

      {/* Roadmap Summary Card */}
      <div
        className="rounded-2xl border p-6"
        style={{
          backgroundColor: 'var(--surface)',
          borderColor: 'var(--border)',
        }}
      >
        <div className="space-y-6">
          {/* Scope */}
          <div>
            <p
              className="text-xs font-medium uppercase tracking-wide"
              style={{
                color: 'var(--text-muted)',
              }}
            >
              Scope
            </p>

            <p
              className="mt-2 text-lg font-medium"
              style={{
                color: 'var(--text-primary)',
              }}
            >
              {roadmap.scope}
            </p>
          </div>

          {/* Progress */}
          <div>
            <div className="flex items-center justify-between">
              <p
                className="text-sm font-medium"
                style={{
                  color: 'var(--text-primary)',
                }}
              >
                Overall progress
              </p>

              <span
                className="text-sm"
                style={{
                  color: 'var(--text-secondary)',
                }}
              >
                {progress}%
              </span>
            </div>

            <div
              className="mt-3 h-2 w-full overflow-hidden rounded-full"
              style={{
                backgroundColor:
                  'var(--border)',
              }}
            >
              <div
                className="h-full rounded-full"
                style={{
                  width: `${progress}%`,
                  backgroundColor:
                    'var(--primary)',
                }}
              />
            </div>

            <p
              className="mt-2 text-xs"
              style={{
                color: 'var(--text-muted)',
              }}
            >
              {completedMissions} of{' '}
              {totalMissions} missions
              completed
            </p>
          </div>

          {/* Current Focus */}
          <div>
            <p
              className="text-xs font-medium uppercase tracking-wide"
              style={{
                color: 'var(--text-muted)',
              }}
            >
              Current Focus
            </p>

            <p
              className="mt-2 text-sm"
              style={{
                color: 'var(--text-primary)',
              }}
            >
              {currentMission
                ? currentMission.title
                : 'No active mission'}
            </p>
          </div>
        </div>
      </div>

      {/* Missions */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h2
              className="text-xl font-semibold"
              style={{
                color: 'var(--text-primary)',
              }}
            >
              Missions
            </h2>

            <p
              className="mt-1 text-sm"
              style={{
                color: 'var(--text-secondary)',
              }}
            >
              Your upcoming learning tasks.
            </p>
          </div>

          <Link
            href="/roadmap"
            className="text-sm font-medium"
            style={{
              color: 'var(--primary)',
            }}
          >
            View all →
          </Link>
        </div>

        <div className="mt-4 space-y-3">
          {visibleMissions.length === 0 ? (
            <div
              className="rounded-2xl border p-5"
              style={{
                backgroundColor:
                  'var(--surface)',
                borderColor:
                  'var(--border)',
              }}
            >
              <p
                className="text-sm"
                style={{
                  color:
                    'var(--text-secondary)',
                }}
              >
                No missions available yet.
              </p>
            </div>
          ) : (
            visibleMissions.map(
              (mission) => {
                const completed =
                  mission.status ===
                  'COMPLETED';

                const inProgress =
                  mission.status ===
                  'IN_PROGRESS';

                return (
                  <Link
                    key={mission.id}
                    href={`/missions/${mission.id}`}
                    className="flex items-center gap-3 rounded-xl border p-4 transition hover:opacity-80"
                    style={{
                      backgroundColor:
                        'var(--surface)',
                      borderColor:
                        'var(--border)',
                    }}
                  >
                    <span
                      className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs"
                      style={{
                        backgroundColor:
                          completed
                            ? 'var(--primary-soft)'
                            : inProgress
                              ? 'var(--feature-blue-soft)'
                              : 'transparent',
                        color:
                          completed
                            ? 'var(--primary)'
                            : inProgress
                              ? 'var(--feature-blue)'
                              : 'var(--text-muted)',
                        borderColor:
                          'var(--border)',
                      }}
                    >
                      {completed
                        ? '✓'
                        : mission.sequence}
                    </span>

                    <span className="min-w-0 flex-1">
                      <span
                        className="block truncate text-sm font-medium"
                        style={{
                          color:
                            'var(--text-primary)',
                        }}
                      >
                        {mission.title}
                      </span>

                      <span
                        className="mt-1 block text-xs"
                        style={{
                          color:
                            'var(--text-muted)',
                        }}
                      >
                        {mission.mission_type}
                        {mission.subject
                          ? ` · ${mission.subject}`
                          : ''}
                        {' · '}
                        {
                          mission.estimated_minutes
                        }{' '}
                        min
                      </span>
                    </span>

                    <span
                      className="shrink-0 text-xs"
                      style={{
                        color:
                          'var(--text-secondary)',
                      }}
                    >
                      {mission.status.replaceAll(
                        '_',
                        ' '
                      )}
                    </span>
                  </Link>
                );
              }
            )
          )}
        </div>
      </div>
    </section>
  );
}
