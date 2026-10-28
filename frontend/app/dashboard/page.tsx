"use client";

import RoadmapSummary from "@/components/roadmap/RoadmapSummary";
import CurrentMissions from "@/components/roadmap/CurrentMissions";
import { useRoadmap } from "@/hooks/useRoadmap";
import { stagger } from "@/components/roadmap/UI";

export default function DashboardPage() {
  const { roadmap } = useRoadmap();

  return (
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

        <div className="grid gap-8 sm:gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)] lg:items-start">
          {roadmap && (
            <div className="rise" style={stagger(1)}>
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
  );
}