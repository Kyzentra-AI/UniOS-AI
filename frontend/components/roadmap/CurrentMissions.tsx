
"use client";

import Link from "next/link";

import type { RoadmapMission } from "@/types/roadmap";

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

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2
            className="text-xl font-semibold"
            style={{ color: "var(--text-primary)" }}
          >
            Current Missions
          </h2>

          <p
            className="mt-1 text-sm"
            style={{ color: "var(--text-secondary)" }}
          >
            Missions that are pending or currently in progress.
          </p>
        </div>

        <Link
          href="/roadmap"
          className="text-sm font-medium"
          style={{ color: "var(--primary)" }}
        >
          View roadmap →
        </Link>
      </div>

      {currentMissions.length === 0 ? (
        <div
          className="rounded-2xl border p-6"
          style={{
            backgroundColor: "var(--surface)",
            borderColor: "var(--border)",
          }}
        >
          <p
            className="text-sm"
            style={{ color: "var(--text-secondary)" }}
          >
            No pending missions right now.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {currentMissions.map((mission) => (
            <Link
              key={mission.id}
              href={`/missions/${mission.id}`}
              className="block rounded-2xl border p-5 transition hover:opacity-80"
              style={{
                backgroundColor: "var(--surface)",
                borderColor: "var(--border)",
              }}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className="text-xs"
                      style={{ color: "var(--text-muted)" }}
                    >
                      Week {mission.week}
                    </span>

                    <span
                      className="text-xs"
                      style={{ color: "var(--text-muted)" }}
                    >
                      ·
                    </span>

                    <span
                      className="text-xs"
                      style={{ color: "var(--text-muted)" }}
                    >
                      Mission {mission.sequence}
                    </span>
                  </div>

                  <h3
                    className="mt-1 text-sm font-semibold"
                    style={{ color: "var(--text-primary)" }}
                  >
                    {mission.title}
                  </h3>

                  <p
                    className="mt-1 text-xs"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    {mission.mission_type}
                    {mission.subject
                      ? ` · ${mission.subject}`
                      : ""}
                    {mission.estimated_minutes != null
                      ? ` · ${mission.estimated_minutes} min`
                      : ""}
                  </p>
                </div>

                <span
                  className="shrink-0 rounded-full px-3 py-1 text-xs font-medium"
                  style={{
                    backgroundColor:
                      mission.status === "IN_PROGRESS"
                        ? "var(--feature-blue-soft)"
                        : "var(--surface-alt)",
                    color:
                      mission.status === "IN_PROGRESS"
                        ? "var(--feature-blue)"
                        : "var(--text-secondary)",
                  }}
                >
                  {mission.status.replaceAll("_", " ")}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
