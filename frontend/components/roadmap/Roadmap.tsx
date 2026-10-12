"use client";

import type {
  Roadmap,
  RoadmapMission,
} from "@/types/roadmap";

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

  const progress =
    missions.length > 0
      ? Math.round((completedMissions / missions.length) * 100)
      : 0;

  return (
    <main
      className="w-full space-y-8"
      style={{ color: "var(--text-primary)" }}
    >
      {/* Header and progress */}
      <section
        className="rounded-2xl border p-6 sm:p-8"
        style={{
          backgroundColor: "var(--surface)",
          borderColor: "var(--border)",
          boxShadow: "0 8px 28px rgba(24, 52, 58, 0.04)",
        }}
      >
        <p
          className="text-xs font-semibold uppercase tracking-[0.16em]"
          style={{ color: "var(--text-muted)" }}
        >
          {roadmap.scope}
        </p>

        <div className="mt-3 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
              Your Learning Roadmap
            </h1>

            <p
              className="mt-2 max-w-xl text-sm leading-6"
              style={{ color: "var(--text-secondary)" }}
            >
              Your learning journey, organized into clear missions and milestones.
            </p>
          </div>

          <span
            className="w-fit rounded-full border px-3 py-1.5 text-xs font-medium"
            style={{
              backgroundColor: "var(--surface-alt)",
              borderColor: "var(--border)",
              color: "var(--text-secondary)",
            }}
          >
            Version {roadmap.version}
          </span>
        </div>

        <div className="mt-8">
          <div className="flex items-center justify-between gap-4">
            <span className="text-sm font-semibold">
              Overall progress
            </span>

            <span
              className="text-sm font-semibold"
              style={{ color: "var(--primary)" }}
            >
              {progress}%
            </span>
          </div>

          <div
            className="mt-3 h-2.5 overflow-hidden rounded-full"
            style={{ backgroundColor: "var(--border)" }}
          >
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${progress}%`,
                backgroundColor: "var(--primary)",
              }}
            />
          </div>

          <div
            className="mt-3 flex flex-wrap items-center justify-between gap-2 text-xs"
            style={{ color: "var(--text-secondary)" }}
          >
            <span>
              {completedMissions} of {missions.length} missions completed
            </span>
            <span>{missions.length - completedMissions} remaining</span>
          </div>
        </div>
      </section>

      {/* Mission list */}
      <section className="space-y-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight">
              Your Missions
            </h2>

            <p
              className="mt-1 text-sm"
              style={{ color: "var(--text-secondary)" }}
            >
              Select a mission to view its details and continue learning.
            </p>
          </div>

          <span
            className="w-fit rounded-full border px-3 py-1.5 text-xs font-medium"
            style={{
              backgroundColor: "var(--surface)",
              borderColor: "var(--border)",
              color: "var(--text-secondary)",
            }}
          >
            {missions.length} missions
          </span>
        </div>

        {missions.length === 0 ? (
          <div
            className="rounded-2xl border p-6"
            style={{
              backgroundColor: "var(--surface)",
              borderColor: "var(--border)",
            }}
          >
            <h3 className="font-semibold">
              No missions available yet
            </h3>

            <p
              className="mt-2 text-sm leading-6"
              style={{ color: "var(--text-secondary)" }}
            >
              Your missions will appear here once your roadmap has been generated.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {missions.map((mission) => (
              <MissionRow
                key={mission.id}
                mission={mission}
                onClick={onMissionClick}
              />
            ))}
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
      className="group flex w-full items-center gap-4 rounded-2xl border p-4 text-left transition duration-200 hover:-translate-y-0.5 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 sm:p-5"
      style={{
        backgroundColor: "var(--surface)",
        borderColor: "var(--border)",
        boxShadow: "0 3px 12px rgba(24, 52, 58, 0.025)",
        outlineColor: "var(--primary)",
      }}
    >
      <span
        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border text-sm font-bold"
        style={{
          backgroundColor: statusBackground,
          borderColor: "var(--border)",
          color: statusColor,
        }}
      >
        {completed ? "✓" : mission.sequence}
      </span>

      <span className="min-w-0 flex-1">
        <span className="block font-semibold leading-5">
          {mission.title}
        </span>

        <span
          className="mt-2 block text-xs leading-5"
          style={{ color: "var(--text-secondary)" }}
        >
          Week {mission.week}
          {" · "}
          {mission.mission_type}
          {mission.subject ? ` · ${mission.subject}` : ""}
          {" · "}
          {mission.estimated_minutes} min
        </span>
      </span>

      <span className="flex shrink-0 flex-col items-end gap-2">
        <span
          className="rounded-full border px-2.5 py-1 text-[10px] font-semibold sm:text-xs"
          style={{
            backgroundColor: statusBackground,
            borderColor: "var(--border)",
            color: statusColor,
          }}
        >
          {statusLabel}
        </span>

        <span
          className="text-lg transition-transform group-hover:translate-x-1"
          style={{ color: "var(--text-muted)" }}
          aria-hidden="true"
        >
          →
        </span>
      </span>
    </button>
  );
}