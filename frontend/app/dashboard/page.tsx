"use client";

import Link from "next/link";

import RoadmapSummary from "@/components/roadmap/RoadmapSummary";
import CurrentMissions from "@/components/roadmap/CurrentMissions";
import { useRoadmap } from "@/hooks/useRoadmap";
import { stagger } from "@/components/roadmap/UI";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function DashboardPage() {
  const {
    roadmap,
    availableSubjects,
  } = useRoadmap();

  const totalMissions = availableSubjects.reduce(
    (sum, subject) => sum + subject.total_missions,
    0
  );

  const completedMissions = availableSubjects.reduce(
    (sum, subject) => sum + subject.completed_missions,
    0
  );

  const overallProgress =
    totalMissions > 0
      ? Math.round(
          (completedMissions / totalMissions) * 100
        )
      : 0;

  return (
    <ProtectedRoute>
      <main className="min-h-screen bg-[radial-gradient(44rem_15rem_at_0%_0%,var(--primary-soft),transparent_70%)] bg-no-repeat px-4 pb-16 pt-6 sm:px-6 sm:pt-12">
        <div className="mx-auto max-w-6xl">
          <header className="rise mb-8 sm:mb-10">
            <h1 className="text-[26px] font-semibold leading-tight tracking-tight text-[var(--text-primary)] sm:text-4xl">
              Welcome to Unios
            </h1>

            <p className="mt-2 max-w-xl text-[15px] leading-6 text-[var(--text-secondary)]">
              Pick up where you left off and keep your learning on track.
            </p>
          </header>

          {availableSubjects.length > 0 && (
            <section
              className="rise mb-9"
              style={stagger(1)}
            >
              <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                    Your Subjects
                  </h2>

                  <p className="mt-1 text-sm text-[var(--text-secondary)]">
                    Track your progress across individual subjects.
                  </p>
                </div>

                <Link
                  href="/roadmap"
                  className="text-sm font-medium text-[var(--primary)] transition hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                >
                  View all subjects
                </Link>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <Link
                  href="/roadmap"
                  className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 transition hover:-translate-y-0.5 hover:shadow-[0_8px_22px_rgba(24,52,58,0.07)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                >
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-semibold text-[var(--text-primary)]">
                      All Subjects
                    </h3>

                    <span className="text-sm font-bold text-[var(--primary)]">
                      {overallProgress}%
                    </span>
                  </div>

                  <p className="mt-1 text-xs text-[var(--text-secondary)]">
                    {completedMissions} of {totalMissions} missions completed
                  </p>

                  <div
                    className="mt-3 h-2 overflow-hidden rounded-full bg-[var(--surface-alt)]"
                    role="progressbar"
                    aria-valuenow={overallProgress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label="All subjects progress"
                  >
                    <div
                      className="bar-grow h-full rounded-full bg-[var(--primary)]"
                      style={{ width: `${overallProgress}%` }}
                    />
                  </div>
                </Link>

                {availableSubjects.map((subject, index) => {
                  const progress = Math.min(
                    100,
                    Math.max(0, subject.progress_percentage)
                  );

                  return (
                    <Link
                      key={subject.name}
                      href={`/roadmap?subject=${encodeURIComponent(subject.name)}`}
                      className="rise rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 transition hover:-translate-y-0.5 hover:shadow-[0_8px_22px_rgba(24,52,58,0.07)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                      style={stagger(index + 2)}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <h3 className="line-clamp-1 font-semibold text-[var(--text-primary)]">
                          {subject.name}
                        </h3>

                        <span className="shrink-0 text-sm font-bold text-[var(--primary)]">
                          {progress}%
                        </span>
                      </div>

                      <p className="mt-1 text-xs text-[var(--text-secondary)]">
                        {subject.completed_missions} of{" "}
                        {subject.total_missions} missions completed
                      </p>

                      <div
                        className="mt-3 h-2 overflow-hidden rounded-full bg-[var(--surface-alt)]"
                        role="progressbar"
                        aria-valuenow={progress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label={`${subject.name} progress`}
                      >
                        <div
                          className="bar-grow h-full rounded-full bg-[var(--primary)]"
                          style={{ width: `${progress}%` }}
                        />
                      </div>

                      {subject.in_progress_missions > 0 && (
                        <p className="mt-2 text-[11px] text-[var(--text-muted)]">
                          {subject.in_progress_missions} currently in progress
                        </p>
                      )}
                    </Link>
                  );
                })}
              </div>
            </section>
          )}

          <div className="grid gap-8 sm:gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)] lg:items-start">
            {roadmap && (
              <div
                className="rise"
                style={stagger(1)}
              >
                <CurrentMissions missions={roadmap.missions} />
              </div>
            )}

            <div
              className={`rise ${roadmap ? "" : "lg:col-span-2 lg:max-w-xl"}`}
              style={stagger(2)}
            >
              <RoadmapSummary />
            </div>
          </div>
        </div>
      </main>
    </ProtectedRoute>
  );
}