
"use client";

import RoadmapSummary from "@/components/roadmap/RoadmapSummary";
import CurrentMissions from "@/components/roadmap/CurrentMissions";

import { useRoadmap } from "@/hooks/useRoadmap";

export default function DashboardPage() {
  const { roadmap } = useRoadmap();

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8">
          <p
            className="text-sm font-medium"
            style={{ color: "var(--text-secondary)" }}
          >
            Command Center
          </p>

          <h1
            className="mt-1 text-3xl font-semibold"
            style={{ color: "var(--text-primary)" }}
          >
            Welcome to Unios
          </h1>

          <p
            className="mt-2 max-w-2xl text-sm"
            style={{ color: "var(--text-secondary)" }}
          >
            Your learning roadmap, current focus, and academic
            progress in one place.
          </p>
        </header>

        <div className="space-y-10">
          <RoadmapSummary />

          {roadmap && (
            <CurrentMissions missions={roadmap.missions} />
          )}
        </div>
      </div>
    </main>
  );
}
