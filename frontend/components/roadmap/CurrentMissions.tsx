"use client";

import Link from "next/link";

import type { RoadmapMission } from "@/types/roadmap";
import { Chevron, Clock, Node, stagger } from "./UI";

interface CurrentMissionsProps {
  missions: RoadmapMission[];
}

export default function CurrentMissions({
  missions,
}: CurrentMissionsProps) {
  const currentMissions = [...missions]
    .filter(
      (mission) =>
        mission.status === "PENDING" ||
        mission.status === "IN_PROGRESS" ||
        mission.status === "DEFERRED"
    )
    .sort((a, b) => {
      if (a.week !== b.week) {
        return a.week - b.week;
      }

      return a.sequence - b.sequence;
    })
    .slice(0, 5);

  const [featured, ...rest] = currentMissions;

  return (
    <section>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-x-4 gap-y-1">
        <div className="min-w-0">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            Current Missions
          </h2>

          <p className="mt-0.5 text-sm text-[var(--text-secondary)]">
            Missions that are pending or currently in progress.
          </p>
        </div>

        <Link
          href="/roadmap"
          className="group inline-flex items-center gap-0.5 rounded-md py-1 text-sm font-medium text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
        >
          View roadmap
          <Chevron className="transition-transform duration-200 group-hover:translate-x-0.5" />
        </Link>
      </div>

      {!featured ? (
        <div className="flex items-center gap-3 rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-6">
          <Node state="done" />
          <p className="text-sm text-[var(--text-secondary)]">
            No pending missions right now.
          </p>
        </div>
      ) : (
        <>
          {/* Featured mission */}
          <Link
            href={`/missions/${featured.id}`}
            className="group relative block overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--primary-soft)] p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_14px_34px_rgba(24,52,58,0.09)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] sm:p-7"
          >
            <span
              aria-hidden="true"
              className="pointer-events-none absolute -right-1 -top-5 hidden select-none text-[130px] font-bold leading-none text-[var(--primary)] opacity-[0.08] transition-transform duration-500 group-hover:-translate-x-1 sm:block"
            >
              {featured.sequence}
            </span>

            <p className="text-xs font-semibold text-[var(--primary)]">
              {featured.status === "IN_PROGRESS"
                ? "Continue where you left off"
                : "Up next"}
              <span className="font-normal text-[var(--text-secondary)]">
                {" · "}Week {featured.week} · Mission {featured.sequence}
              </span>
            </p>

            <h3 className="relative mt-2.5 max-w-xl text-xl font-semibold leading-snug text-[var(--text-primary)] sm:text-2xl">
              {featured.title}
            </h3>

            <div className="relative mt-4 flex flex-wrap gap-2 text-xs text-[var(--text-secondary)]">
              <span className="rounded-full bg-[var(--surface)] px-2.5 py-1">
                {featured.mission_type}
              </span>
              {featured.subject && (
                <span className="rounded-full bg-[var(--surface)] px-2.5 py-1">
                  {featured.subject}
                </span>
              )}
              {featured.estimated_minutes != null && (
                <span className="inline-flex items-center gap-1 rounded-full bg-[var(--surface)] px-2.5 py-1">
                  <Clock />
                  {featured.estimated_minutes} min
                </span>
              )}
            </div>

            <span className="relative mt-6 inline-flex w-full items-center justify-center gap-1 rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-[var(--surface)] transition-[padding] duration-200 group-hover:pr-4 sm:w-auto">
              {featured.status === "IN_PROGRESS" ? "Continue" : "Start mission"}
              <Chevron className="transition-transform duration-200 group-hover:translate-x-1" />
            </span>
          </Link>

          {/* Queue */}
          {rest.length > 0 && (
            <div className="mt-8">
              <h3 className="mb-3 text-sm font-semibold text-[var(--text-secondary)]">
                After that
              </h3>

              <ol className="relative">
                <span
                  aria-hidden="true"
                  className="line-grow absolute bottom-6 left-[14px] top-6 w-px bg-[var(--border)]"
                />

                {rest.map((mission, i) => {
                  const inProgress = mission.status === "IN_PROGRESS";

                  return (
                    <li
                      key={mission.id}
                      className="rise relative pb-2.5 pl-11 last:pb-0"
                      style={stagger(i + 2)}
                    >
                      <span className="absolute left-0 top-3.5">
                        <Node state={inProgress ? "active" : "idle"}>
                          {mission.sequence}
                        </Node>
                      </span>

                      <Link
                        href={`/missions/${mission.id}`}
                        className="group block rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 transition duration-200 hover:-translate-y-px hover:shadow-[0_8px_22px_rgba(24,52,58,0.07)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <p className="text-xs text-[var(--text-muted)]">
                              Week {mission.week} · Mission {mission.sequence}
                            </p>

                            <h4 className="mt-0.5 line-clamp-2 text-sm font-semibold text-[var(--text-primary)]">
                              {mission.title}
                            </h4>

                            <p className="mt-1 text-xs text-[var(--text-secondary)]">
                              {mission.mission_type}
                              {mission.subject ? ` · ${mission.subject}` : ""}
                              {mission.estimated_minutes != null
                                ? ` · ${mission.estimated_minutes} min`
                                : ""}
                            </p>
                          </div>

                          <Chevron className="mt-1 shrink-0 text-[var(--text-muted)] transition-transform duration-200 group-hover:translate-x-0.5" />
                        </div>

                        <span
                          className="mt-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
                          style={{
                            backgroundColor: inProgress
                              ? "var(--feature-blue-soft)"
                              : "var(--surface-alt)",
                            color: inProgress
                              ? "var(--feature-blue)"
                              : "var(--text-secondary)",
                          }}
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-current" />
                          {mission.status.replaceAll("_", " ")}
                        </span>
                      </Link>
                    </li>
                  );
                })}
              </ol>
            </div>
          )}
        </>
      )}
    </section>
  );
}