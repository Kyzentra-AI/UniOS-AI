"use client";

import type {
  Roadmap,
  RoadmapMission,
} from "@/types/roadmap";
import { Chevron, Node, ProgressRing, stagger } from "./UI";

interface RoadmapProps {
  roadmap: Roadmap;
  onMissionClick?: (mission: RoadmapMission) => void;
}

export default function Roadmap({
  roadmap,
  onMissionClick,
}: RoadmapProps) {
  const missions = [...roadmap.missions].sort((a, b) => {
    if (a.week !== b.week) {
      return a.week - b.week;
    }

    return a.sequence - b.sequence;
  });

  const completedMissions = missions.filter(
    (mission) => mission.status === "COMPLETED"
  ).length;

  const inProgressMissions = missions.filter(
    (mission) => mission.status === "IN_PROGRESS"
  ).length;

  const progress =
    missions.length > 0
      ? Math.round((completedMissions / missions.length) * 100)
      : 0;

  const weeks = missions.reduce<{ week: number; items: RoadmapMission[] }[]>(
    (acc, mission) => {
      const last = acc[acc.length - 1];
      if (last && last.week === mission.week) last.items.push(mission);
      else acc.push({ week: mission.week, items: [mission] });
      return acc;
    },
    []
  );

  let nodeIndex = 0;

  return (
    <main className="w-full space-y-10 text-[var(--text-primary)]">
      {/* Header and progress */}
      <section className="rise">
        <p className="text-sm text-[var(--text-secondary)]">
          {roadmap.scope}
        </p>

        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-2">
          <h1 className="text-[26px] font-bold leading-tight tracking-tight sm:text-3xl">
            Your Learning Roadmap
          </h1>

          <span className="rounded-full border border-[var(--border)] bg-[var(--surface-alt)] px-2.5 py-1 text-xs font-medium text-[var(--text-secondary)]">
            Version {roadmap.version}
          </span>
        </div>

        <p className="mt-2 max-w-xl text-sm leading-6 text-[var(--text-secondary)]">
          Your learning journey, organized into clear missions and milestones.
        </p>

        <div
          className="rise mt-6 rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-7"
          style={stagger(1)}
        >
          <div className="flex flex-col items-center gap-6 sm:flex-row sm:gap-8">
            <ProgressRing value={progress} size={120} stroke={10} />

            <div className="w-full min-w-0 flex-1">
              <p className="text-sm font-semibold">Overall progress</p>

              <div className="mt-3 grid grid-cols-3 divide-x divide-[var(--border)] text-center sm:text-left">
                {[
                  { label: "Completed", value: completedMissions },
                  { label: "In progress", value: inProgressMissions },
                  { label: "Remaining", value: missions.length - completedMissions },
                ].map((stat, i) => (
                  <div key={stat.label} className={i > 0 ? "px-2 sm:px-5" : "pr-2 sm:pr-5"}>
                    <p className="text-2xl font-bold tracking-tight sm:text-3xl">{stat.value}</p>
                    <p className="mt-0.5 text-xs text-[var(--text-secondary)]">{stat.label}</p>
                  </div>
                ))}
              </div>

              {/* One segment per mission */}
              <div
                className="mt-5 flex gap-[3px]"
                role="img"
                aria-label={`${completedMissions} of ${missions.length} missions completed`}
              >
                {missions.map((mission, i) => (
                  <span
                    key={mission.id}
                    className="seg h-2 flex-1 rounded-full"
                    style={{
                      ...stagger(Math.min(i, 40)),
                      backgroundColor:
                        mission.status === "COMPLETED"
                          ? "var(--primary)"
                          : mission.status === "IN_PROGRESS"
                            ? "var(--feature-orange)"
                            : "var(--border)",
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission timeline */}
      <section>
        <div className="mb-6 flex flex-wrap items-end justify-between gap-x-4 gap-y-2">
          <div className="min-w-0">
            <h2 className="text-xl font-bold tracking-tight">
              Your Missions
            </h2>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Select a mission to view its details and continue learning.
            </p>
          </div>

          <span className="shrink-0 rounded-full border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1 text-xs font-medium text-[var(--text-secondary)]">
            {missions.length} missions
          </span>
        </div>

        {missions.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-8 text-center">
            <h3 className="font-semibold">No missions available yet</h3>

            <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-[var(--text-secondary)]">
              Your missions will appear here once your roadmap has been generated.
            </p>
          </div>
        ) : (
          <div className="space-y-8 md:space-y-10">
            {weeks.map(({ week, items }) => {
              const done = items.filter((m) => m.status === "COMPLETED").length;

              return (
                <div
                  key={week}
                  className="reveal md:grid md:grid-cols-[7.5rem_minmax(0,1fr)] md:gap-6"
                >
                  {/* Week label */}
                  <div className="mb-3 flex items-baseline justify-between md:sticky md:top-6 md:mb-0 md:block md:self-start md:pt-3">
                    <h3 className="text-base font-bold">Week {week}</h3>
                    <p className="text-xs text-[var(--text-secondary)] md:mt-0.5">
                      {done} of {items.length} done
                    </p>
                  </div>

                  <ol className="relative">
                    <span
                      aria-hidden="true"
                      className="line-grow absolute bottom-8 left-[14px] top-8 w-px bg-[var(--border)]"
                    />

                    {items.map((mission) => {
                      const idx = Math.min(nodeIndex++, 8);
                      return (
                        <li
                          key={mission.id}
                          className="relative pb-2.5 pl-11 last:pb-0"
                          style={stagger(idx)}
                        >
                          <span className="absolute left-0 top-[18px]">
                            <Node
                              tone="orange"
                              state={
                                mission.status === "COMPLETED"
                                  ? "done"
                                  : mission.status === "IN_PROGRESS"
                                    ? "active"
                                    : "idle"
                              }
                            >
                              {mission.sequence}
                            </Node>
                          </span>

                          <MissionRow mission={mission} onClick={onMissionClick} />
                        </li>
                      );
                    })}
                  </ol>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}

interface MissionRowProps {
  mission: RoadmapMission;
  onClick?: (mission: RoadmapMission) => void;
}

function MissionRow({
  mission,
  onClick,
}: MissionRowProps) {
  const completed = mission.status === "COMPLETED";
  const inProgress = mission.status === "IN_PROGRESS";

  const statusLabel = mission.status.replaceAll("_", " ");

  const statusColor = completed
    ? "var(--primary)"
    : inProgress
      ? "var(--feature-orange)"
      : "var(--text-secondary)";

  const statusBackground = completed
    ? "var(--primary-soft)"
    : inProgress
      ? "var(--feature-orange-soft)"
      : "var(--surface-alt)";

  return (
    <button
      type="button"
      onClick={() => onClick?.(mission)}
      className="group flex w-full items-start gap-3 rounded-2xl border bg-[var(--surface)] p-4 text-left shadow-[0_3px_12px_rgba(24,52,58,0.025)] transition duration-200 hover:-translate-y-px hover:shadow-[0_10px_26px_rgba(24,52,58,0.08)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] sm:items-center sm:p-5"
      style={{ borderColor: inProgress ? "var(--feature-orange)" : "var(--border)" }}
    >
      <span className="min-w-0 flex-1">
        <span
          className={`line-clamp-2 block font-semibold leading-5 ${
            completed ? "text-[var(--text-secondary)]" : ""
          }`}
        >
          {mission.title}
        </span>

        <span className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1.5 text-xs leading-5 text-[var(--text-secondary)]">
          <span>
            {mission.mission_type}
            {mission.subject ? ` · ${mission.subject}` : ""}
            {mission.estimated_minutes != null
              ? ` · ${mission.estimated_minutes} min`
              : ""}
          </span>

          <span
            className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-semibold"
            style={{ backgroundColor: statusBackground, color: statusColor }}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-current" />
            {statusLabel}
          </span>
        </span>
      </span>

      <Chevron className="mt-0.5 shrink-0 text-[var(--text-muted)] transition-transform duration-200 group-hover:translate-x-0.5 sm:mt-0" />
    </button>
  );
}