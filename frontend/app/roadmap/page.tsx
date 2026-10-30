"use client";

import Roadmap from "@/components/roadmap/Roadmap";
import { useRoadmap } from "@/hooks/useRoadmap";
import { useRouter } from "next/navigation";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function RoadmapPage() {
  const router = useRouter();
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
    <ProtectedRoute>
    <main className="flex min-h-[70vh] items-center justify-center px-6">
      <div className="flex flex-col items-center text-center">
        <div className="relative flex h-14 w-14 items-center justify-center">
          <div className="absolute inset-0 rounded-full border-[3px] border-[var(--border)]" />
          <div className="absolute inset-0 animate-spin rounded-full border-[3px] border-transparent border-t-[var(--primary)]" />
          <div className="h-2.5 w-2.5 rounded-full bg-[var(--primary)]" />
        </div>

        <h2 className="mt-6 text-base font-semibold text-[var(--text-primary)]">
          Preparing your roadmap
        </h2>

        <p className="mt-2 max-w-xs text-sm leading-6 text-[var(--text-secondary)]">
          Loading your learning journey. This will only take a moment.
        </p>
      </div>
    </main>
    </ProtectedRoute>
  );
}

  if (isError) {
    return (
      <ProtectedRoute>
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
      </ProtectedRoute>
    );
  }

  if (!roadmap) {
    return (
      <ProtectedRoute>
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
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-6xl">
        <Roadmap
  roadmap={roadmap}
  onMissionClick={(mission) => {
    router.push(`/missions/${mission.id}`);
  }}
/>
      </div>
    </main>
    </ProtectedRoute>
  );
}