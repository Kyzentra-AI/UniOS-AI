
"use client";

import Link from "next/link";
import type { Mission } from "@/types/mission";
import { Check } from "@/components/roadmap/UI";

interface MissionCardProps {
  mission: Mission;
  onStart?: () => void;
  onComplete?: () => void;
  onDefer?: () => void;
  onSkip?: () => void;
  isStarting?: boolean;
  isCompleting?: boolean;
  isDeferring?: boolean;
  isSkipping?: boolean;
}

type OverviewSection = {
  title: string;
  items: string[];
};

type MissionData = Mission & Record<string, unknown>;

const SECTION_ALIASES: Record<string, string[]> = {
  "Objectives": ["objectives", "objective", "learning_objectives"],
  "Core Concepts": ["core_concepts", "core concepts", "concepts", "topics"],
  "Deliverables": ["deliverables", "tasks", "outputs"],
  "Mastery Criteria": [
    "mastery_criteria",
    "mastery criteria",
    "success_criteria",
    "success criteria",
  ],
};

function normalizeItems(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .flatMap((item) => normalizeItems(item))
      .filter(Boolean);
  }

  if (typeof value !== "string") return [];

  return value
    .split(/\r?\n/)
    .map((item) => item.replace(/^\s*(?:[-*•]|\d+[.)])\s*/, "").trim())
    .filter(Boolean);
}

function getStructuredSections(
  mission: MissionData,
): OverviewSection[] {
  const sections: OverviewSection[] = [];

  for (const [title, aliases] of Object.entries(SECTION_ALIASES)) {
    const key = aliases.find(
      (alias) => mission[alias] !== undefined && mission[alias] !== null,
    );

    if (!key) continue;

    const items = normalizeItems(mission[key]);

    if (items.length) {
      sections.push({ title, items });
    }
  }

  return sections;
}

function parseLegacyDescription(description: string): {
  sections: OverviewSection[];
  summary: string;
} {
  const lines = description.split(/\r?\n/);
  const sections: OverviewSection[] = [];
  const summaryLines: string[] = [];

  const aliases = new Map<string, string>();

  for (const [title, keys] of Object.entries(SECTION_ALIASES)) {
    keys.forEach((key) => aliases.set(key.toLowerCase(), title));
    aliases.set(title.toLowerCase(), title);
  }

  let activeTitle: string | null = null;
  let activeItems: string[] = [];

  const flush = () => {
    if (activeTitle && activeItems.length) {
      sections.push({
        title: activeTitle,
        items: activeItems,
      });
    }

    activeTitle = null;
    activeItems = [];
  };

  for (const line of lines) {
    const trimmed = line.trim();

    if (!trimmed) {
      if (!activeTitle) summaryLines.push("");
      continue;
    }

    const heading = trimmed
      .replace(/^#{1,4}\s*/, "")
      .replace(/[:*]+$/, "")
      .trim()
      .toLowerCase();

    const matchedTitle = aliases.get(heading);

    if (matchedTitle) {
      flush();
      activeTitle = matchedTitle;
      continue;
    }

    const inlineHeading = trimmed.match(
      /^(?:#{1,4}\s*)?([^:]{2,40}):\s*(.*)$/,
    );

    const inlineTitle = inlineHeading
      ? aliases.get(inlineHeading[1].trim().toLowerCase())
      : undefined;

    if (inlineHeading && inlineTitle) {
      flush();
      activeTitle = inlineTitle;

      if (inlineHeading[2].trim()) {
        activeItems.push(
          inlineHeading[2].replace(/^[-*•]\s*/, "").trim(),
        );
      }

      continue;
    }

    const item = trimmed.replace(/^[-*•]\s*/, "").replace(/^\d+[.)]\s*/, "");

    if (activeTitle) {
      activeItems.push(item);
    } else {
      summaryLines.push(trimmed);
    }
  }

  flush();

  return {
    sections,
    summary: summaryLines.join("\n").trim(),
  };
}

function getMissionOverview(mission: MissionData) {
  let description =
    typeof mission.description === "string"
      ? mission.description.trim()
      : "";

  // Support a JSON-formatted description without requiring a new API contract.
  if (description.startsWith("{")) {
    try {
      const parsed = JSON.parse(description) as Record<string, unknown>;

      const parsedSections = getStructuredSections(
        parsed as MissionData,
      );

      const structured = getStructuredSections(mission);

      return {
        sections: structured.length ? structured : parsedSections,
        summary:
          typeof parsed.description === "string"
            ? parsed.description
            : typeof parsed.summary === "string"
              ? parsed.summary
              : "",
      };
    } catch {
      // Continue with legacy text parsing.
    }
  }

  const legacy = parseLegacyDescription(description);
  const structured = getStructuredSections(mission);

  return {
    sections: structured.length ? structured : legacy.sections,
    summary: legacy.summary,
  };
}

function OverviewSectionCard({
  section,
}: {
  section: OverviewSection;
}) {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4">
      <h4 className="text-sm font-semibold text-[var(--text-primary)]">
        {section.title}
      </h4>

      <ul className="mt-3 space-y-2">
        {section.items.map((item, index) => (
          <li
            key={`${section.title}-${index}`}
            className="flex items-start gap-2 text-sm leading-6 text-[var(--text-secondary)]"
          >
            <span
              className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full"
              style={{ backgroundColor: "var(--primary)" }}
            />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function MissionCard({
  mission,
  onStart,
  onComplete,
  onDefer,
  onSkip,
  isStarting = false,
  isCompleting = false,
  isDeferring = false,
  isSkipping = false,
}: MissionCardProps) {
  const isCompleted = mission.status === "COMPLETED";
  const isInProgress = mission.status === "IN_PROGRESS";
  const isPending = mission.status === "PENDING";
  const isDeferred = mission.status === "DEFERRED";
  const isSkipped = mission.status === "SKIPPED";

  const isBusy =
    isStarting || isCompleting || isDeferring || isSkipping;

  const overview = getMissionOverview(mission as MissionData);

  return (
    <article
      className="rounded-2xl border p-5 sm:p-6"
      style={{
        background: "var(--surface)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 gap-3">
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-semibold"
            style={{
              background: "var(--primary-soft)",
              color: "var(--primary)",
            }}
          >
            {mission.sequence ?? "—"}
          </div>

          <div className="min-w-0">
            <p
              className="text-xs font-medium uppercase tracking-wide"
              style={{ color: "var(--text-muted)" }}
            >
              Mission
            </p>

            <h3
              className="mt-1 text-base font-semibold"
              style={{ color: "var(--text-primary)" }}
            >
              {mission.title}
            </h3>
          </div>
        </div>

        <span
          className="inline-flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium"
          style={{
            background: isCompleted
              ? "var(--primary-soft)"
              : isInProgress
                ? "var(--feature-blue-soft)"
                : "var(--surface-alt)",
            color: isCompleted
              ? "var(--primary)"
              : isInProgress
                ? "var(--feature-blue)"
                : "var(--text-secondary)",
          }}
        >
          {isCompleted ? (
            <Check className="check-reveal" />
          ) : (
            <span
              className={`h-1.5 w-1.5 rounded-full bg-current ${
                isInProgress ? "pulse" : ""
              }`}
            />
          )}

          {mission.status.replaceAll("_", " ")}
        </span>
      </div>

      <div className="mt-6 space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-[var(--text-primary)]">
            Mission Overview
          </h4>

          {overview.summary && (
            <p className="mt-2 whitespace-pre-line text-sm leading-7 text-[var(--text-secondary)]">
              {overview.summary}
            </p>
          )}

          {!overview.summary && overview.sections.length === 0 && (
            <p className="mt-2 text-sm text-[var(--text-muted)]">
              No additional mission description is available.
            </p>
          )}
        </div>

        {overview.sections.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {overview.sections.map((section) => (
              <OverviewSectionCard
                key={section.title}
                section={section}
              />
            ))}
          </div>
        )}
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {mission.mission_type && (
          <span
            className="rounded-lg px-2.5 py-1 text-xs"
            style={{
              background: "var(--surface-alt)",
              color: "var(--text-secondary)",
            }}
          >
            {mission.mission_type}
          </span>
        )}

        {mission.subject && (
          <Link
            href={`/roadmap?subject=${encodeURIComponent(mission.subject)}`}
            className="rounded-lg px-2.5 py-1 text-xs transition hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
            style={{
              background: "var(--surface-alt)",
              color: "var(--primary)",
            }}
          >
            {mission.subject}
          </Link>
        )}

        {mission.estimated_minutes != null && (
          <span
            className="rounded-lg px-2.5 py-1 text-xs"
            style={{
              background: "var(--surface-alt)",
              color: "var(--text-secondary)",
            }}
          >
            {mission.estimated_minutes} min
          </span>
        )}
      </div>

      <div
        className="mt-5 flex flex-col gap-4 border-t pt-4 sm:flex-row sm:items-center sm:justify-between"
        style={{ borderColor: "var(--border)" }}
      >
        <span
          className="text-xs"
          style={{ color: "var(--text-muted)" }}
        >
          {isCompleted
            ? "Mission completed"
            : isInProgress
              ? "Currently in progress"
              : isDeferred
                ? "Mission deferred"
                : isSkipped
                  ? "Mission skipped"
                  : "Ready to start"}
        </span>

        <div className="flex flex-wrap items-center justify-end gap-2">
          {isPending || isDeferred ? (
            <button
              type="button"
              onClick={onStart}
              disabled={isBusy || !onStart}
              className="rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50"
              style={{
                background: "var(--primary)",
                color: "var(--surface)",
              }}
            >
              {isStarting ? "Starting..." : "Start Mission"}
            </button>
          ) : null}

          {isInProgress ? (
            <>
              {onDefer && (
                <button
                  type="button"
                  onClick={onDefer}
                  disabled={isBusy}
                  className="rounded-xl border px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50"
                  style={{
                    borderColor: "var(--border)",
                    color: "var(--text-secondary)",
                  }}
                >
                  {isDeferring ? "Deferring..." : "Defer"}
                </button>
              )}

              {onSkip && (
                <button
                  type="button"
                  onClick={onSkip}
                  disabled={isBusy}
                  className="rounded-xl border px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50"
                  style={{
                    borderColor: "var(--border)",
                    color: "var(--text-secondary)",
                  }}
                >
                  {isSkipping ? "Skipping..." : "Skip"}
                </button>
              )}

              <button
                type="button"
                onClick={onStart}
                disabled={isBusy || !onStart}
                className="rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50"
                style={{
                  background: "var(--primary)",
                  color: "var(--surface)",
                }}
              >
                {isStarting ? "Resuming..." : "Continue Mission"}
              </button>

              <button
                type="button"
                onClick={onComplete}
                disabled={isBusy || !onComplete}
                className="rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50"
                style={{
                  background: "var(--primary)",
                  color: "var(--surface)",
                }}
              >
                {isCompleting ? "Completing..." : "Complete Mission"}
              </button>
            </>
          ) : null}
        </div>
      </div>
    </article>
  );
}
