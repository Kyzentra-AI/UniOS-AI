"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import Roadmap from "@/components/roadmap/Roadmap";
import SubjectTabs from "@/components/roadmap/SubjectTabs";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useRoadmap } from "@/hooks/useRoadmap";

function RoadmapPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const subject = searchParams?.get("subject")?.trim() ?? null;

  const {
    roadmap,
    availableSubjects,
    activeSubject,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useRoadmap({ subject });

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-6xl">
        <header className="rise mb-7">
          <p className="text-sm text-[var(--text-secondary)]">
            Your learning journey
          </p>

          <h1 className="mt-1 text-2xl font-bold tracking-tight text-[var(--text-primary)] sm:text-3xl">
            Your Roadmap
          </h1>
        </header>

        {!isLoading && (
          <SubjectTabs
            subjects={availableSubjects}
            selectedSubject={subject}
            activeSubject={activeSubject}
          />
        )}

        {isLoading ? (
          <div className="flex min-h-[45vh] items-center justify-center">
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
          </div>
        ) : isError ? (
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="font-semibold text-[var(--text-primary)]">
              Unable to load your roadmap.
            </h2>

            <p className="mt-2 text-sm text-[var(--text-secondary)]">
              {error instanceof Error
                ? error.message
                : "Something went wrong."}
            </p>

            <button
              type="button"
              onClick={() => refetch()}
              className="mt-4 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-[var(--surface)] transition hover:opacity-90"
            >
              Try again
            </button>
          </section>
        ) : !roadmap ? (
          <section className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-8">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              {subject
                ? `No roadmap for ${subject}`
                : "Your roadmap is being prepared"}
            </h2>

            <p className="mt-2 max-w-lg text-sm leading-6 text-[var(--text-secondary)]">
              {subject
                ? "There are currently no missions available for this subject. Select another subject or view all subjects."
                : "Your roadmap will appear here once it has been generated."}
            </p>

            {isFetching && (
              <p className="mt-3 text-xs text-[var(--text-muted)]">
                Checking for your roadmap...
              </p>
            )}

            {subject && (
              <button
                type="button"
                onClick={() => router.push("/roadmap")}
                className="mt-5 rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-medium text-[var(--surface)] transition hover:opacity-90"
              >
                View all subjects
              </button>
            )}
          </section>
        ) : (
          <Roadmap
            roadmap={roadmap}
            onMissionClick={(mission) => {
              router.push(`/missions/${mission.id}`);
            }}
          />
        )}
      </div>
    </main>
  );
}

export default function RoadmapPage() {
  return (
    <ProtectedRoute>
      <Suspense
        fallback={
          <main className="flex min-h-[70vh] items-center justify-center px-6">
            <p className="text-sm text-[var(--text-secondary)]">
              Loading roadmap...
            </p>
          </main>
        }
      >
        <RoadmapPageContent />
      </Suspense>
    </ProtectedRoute>
  );
}