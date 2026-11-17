"use client";

import Link from "next/link";

import type { RoadmapSubjectSummary } from "@/types/roadmap";

interface SubjectTabsProps {
  subjects: RoadmapSubjectSummary[];
  selectedSubject?: string | null;
  activeSubject?: string | null;
}

export default function SubjectTabs({
  subjects,
  selectedSubject = null,
  activeSubject = null,
}: SubjectTabsProps) {
  const selected = selectedSubject?.trim() || null;

  const totalMissions = subjects.reduce(
    (sum, item) => sum + item.total_missions,
    0
  );

  const completedMissions = subjects.reduce(
    (sum, item) => sum + item.completed_missions,
    0
  );

  const overallProgress =
    totalMissions > 0
      ? Math.round((completedMissions / totalMissions) * 100)
      : 0;

  const tabs = [
    {
      name: "All Subjects",
      href: "/roadmap",
      isActive: selected === null,
      total: totalMissions,
      progress: overallProgress,
    },
    ...subjects.map((item) => ({
      name: item.name,
      href: `/roadmap?subject=${encodeURIComponent(item.name)}`,
      isActive: selected === item.name,
      total: item.total_missions,
      progress: item.progress_percentage,
    })),
  ];

  return (
    <section
      className="mb-8"
      aria-label="Filter roadmap by subject"
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold text-[var(--text-primary)]">
            Subjects
          </h2>
          <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
            Track progress across all subjects or focus on one.
          </p>
        </div>

        {activeSubject && activeSubject !== "ALL" && (
          <span className="text-xs text-[var(--text-muted)]">
            Active subject: {activeSubject}
          </span>
        )}
      </div>

      <nav
        className="flex gap-2 overflow-x-auto pb-2"
        aria-label="Roadmap subjects"
      >
        {tabs.map((tab) => (
          <Link
            key={tab.name}
            href={tab.href}
            aria-current={tab.isActive ? "page" : undefined}
            className={`inline-flex shrink-0 flex-col gap-1 rounded-2xl border px-4 py-2.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] ${
              tab.isActive
                ? "border-[var(--primary)] bg-[var(--primary)] text-[var(--surface)]"
                : "border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)] hover:bg-[var(--surface-alt)]"
            }`}
          >
            <span className="flex items-center gap-2 text-sm font-semibold">
              {tab.name}
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] ${
                  tab.isActive
                    ? "bg-[var(--surface)]/15 text-[var(--surface)]"
                    : "bg-[var(--surface-alt)] text-[var(--text-muted)]"
                }`}
              >
                {tab.total}
              </span>
            </span>

            <span
              className={`text-[11px] ${
                tab.isActive
                  ? "text-[var(--surface)]/80"
                  : "text-[var(--text-muted)]"
              }`}
            >
              {tab.progress}% completed
            </span>
          </Link>
        ))}
      </nav>
    </section>
  );
}