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
  const scopeData = roadmap.scope_data;

  const missions = [...roadmap.missions].sort(
    (a, b) => {
      if (a.week !== b.week) {
        return a.week - b.week;
      }

      return a.sequence - b.sequence;
    }
  );

  return (
    <section className="w-full space-y-8">
      {/* Header */}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide opacity-50">
          {roadmap.scope}
        </p>

        <h1 className="mt-1 text-2xl font-semibold">
          Your Roadmap
        </h1>

        <p className="mt-1 text-sm opacity-65">
          Roadmap version {roadmap.version}
        </p>
      </div>

      {/* Academic roadmap */}
      {scopeData.semesters.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold">
            Academic Roadmap
          </h2>

          {scopeData.semesters.map((semester) => (
            <div
              key={semester.name}
              className="rounded-2xl border p-5"
            >
              <h3 className="font-medium">
                {semester.name}
              </h3>

              <div className="mt-4 space-y-4">
                {semester.subjects.map((subject) => (
                  <div key={subject.name}>
                    <p className="text-sm font-medium">
                      {subject.name}
                    </p>

                    {subject.topics.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {subject.topics.map((topic) => (
                          <span
                            key={topic}
                            className="rounded-lg border px-3 py-1.5 text-xs opacity-75"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </section>
      )}

      {/* Career */}
      {scopeData.career && (
        <section className="rounded-2xl border p-5">
          <h2 className="text-lg font-semibold">
            Career Goals
          </h2>

          <div className="mt-4 space-y-2">
            {scopeData.career.goals.map((goal) => (
              <div
                key={goal}
                className="rounded-xl border p-3 text-sm"
              >
                {goal}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Goals */}
      {scopeData.goals.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold">
            Goals
          </h2>

          <div className="mt-4 space-y-2">
            {scopeData.goals.map((goal) => (
              <div
                key={goal}
                className="rounded-xl border p-4 text-sm"
              >
                {goal}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Milestones */}
      {scopeData.milestones.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold">
            Milestones
          </h2>

          <div className="mt-4 space-y-2">
            {scopeData.milestones.map((milestone) => (
              <div
                key={milestone}
                className="rounded-xl border p-4 text-sm"
              >
                {milestone}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Missions */}
      <section>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            Missions
          </h2>

          <span className="text-sm opacity-60">
            {missions.length} missions
          </span>
        </div>

        <div className="mt-4 space-y-3">
          {missions.length === 0 ? (
            <div className="rounded-2xl border p-5 text-sm opacity-60">
              No missions available yet.
            </div>
          ) : (
            missions.map((mission) => (
              <MissionRow
                key={mission.id}
                mission={mission}
                onClick={onMissionClick}
              />
            ))
          )}
        </div>
      </section>
    </section>
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
  const completed =
    mission.status === "COMPLETED";

  return (
    <button
      type="button"
      onClick={() => onClick?.(mission)}
      className="flex w-full items-center gap-3 rounded-xl border p-4 text-left transition hover:opacity-80"
    >
      <span
        className={[
          "flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs",
          completed
            ? "opacity-100"
            : "opacity-50",
        ].join(" ")}
      >
        {completed ? "✓" : ""}
      </span>

      <span className="min-w-0 flex-1">
        <span className="block text-sm font-medium">
          {mission.title}
        </span>

        <span className="mt-1 block text-xs opacity-55">
          {mission.mission_type}
          {mission.subject
            ? ` · ${mission.subject}`
            : ""}
          {" · "}
          {mission.estimated_minutes} min
        </span>
      </span>

      <span className="text-xs opacity-55">
        {mission.status}
      </span>
    </button>
  );
}