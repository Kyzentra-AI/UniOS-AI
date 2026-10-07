"use client";

import Roadmap from "@/components/roadmap/Roadmap";
import { useRoadmap } from "@/hooks/useRoadmap";

export default function RoadmapPage() {
  const {
    roadmap,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useRoadmap();

  if (isLoading) {
    return (
      <main className="min-h-screen px-6 py-8">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm opacity-60">
            Loading your roadmap...
          </p>
        </div>
      </main>
    );
  }

  if (isError) {
    return (
      <main className="min-h-screen px-6 py-8">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm">
            Unable to load your roadmap.
          </p>

          <p className="mt-1 text-xs opacity-60">
            {error instanceof Error
              ? error.message
              : "Something went wrong."}
          </p>

          <button
            type="button"
            onClick={() => refetch()}
            className="mt-4 rounded-lg border px-4 py-2 text-sm"
          >
            Try again
          </button>
        </div>
      </main>
    );
  }

  if (!roadmap) {
    return (
      <main className="min-h-screen px-6 py-8">
        <div className="mx-auto max-w-6xl">
          <h1 className="text-2xl font-semibold">
            Your Roadmap
          </h1>

          <p className="mt-2 text-sm opacity-60">
            Your roadmap is being prepared or has not been
            generated yet.
          </p>

          {isFetching && (
            <p className="mt-2 text-xs opacity-50">
              Checking for your roadmap...
            </p>
          )}
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-6xl">
        <Roadmap
          roadmap={roadmap}
          onMissionClick={(mission) => {
            console.log(
              "Selected mission:",
              mission.id
            );
          }}
        />
      </div>
    </main>
  );
}