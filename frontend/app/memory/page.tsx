
"use client";

import {
  BookOpen,
  BriefcaseBusiness,
  GraduationCap,
  Brain,
  Clock3,
  Lightbulb,
  RefreshCw,
  UserRound,
  Target,
  Sparkles,
  FolderKanban,
  AlertCircle,
  ChevronRight,
} from "lucide-react";

import { useProfile } from "@/hooks/useProfile";

function SectionCard({
  title,
  description,
  icon: Icon,
  children,
}: {
  title: string;
  description?: string;
  icon: React.ElementType;
  children: React.ReactNode;
}) {
  return (
    <section className="group min-w-0 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_2px_10px_rgba(24,52,58,0.025)] transition-all duration-200 hover:border-[var(--primary)]/30 hover:shadow-[0_8px_24px_rgba(24,52,58,0.05)] sm:p-6">
      <div className="mb-5 flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[var(--primary)]/10 bg-[var(--primary)]/[0.07] text-[var(--primary)]">
          <Icon size={19} strokeWidth={1.8} />
        </div>

        <div className="min-w-0">
          <h2 className="text-base font-semibold tracking-tight text-[var(--text-primary)]">
            {title}
          </h2>

          {description && (
            <p className="mt-1 text-sm leading-5 text-[var(--text-secondary)]">
              {description}
            </p>
          )}
        </div>
      </div>

      {children}
    </section>
  );
}

function Detail({
  label,
  value,
}: {
  label: string;
  value?: string | number | null;
}) {
  const displayValue =
    value !== undefined && value !== null && String(value).trim()
      ? String(value)
      : "Not provided";

  return (
    <div className="min-w-0 rounded-xl border border-[var(--border)]/70 bg-[var(--background)] p-3.5 transition-colors hover:border-[var(--primary)]/20">
      <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-[var(--text-muted)]">
        {label}
      </p>

      <p className="break-words text-sm font-medium leading-5 text-[var(--text-primary)]">
        {displayValue}
      </p>
    </div>
  );
}

function TagList({
  items,
  emptyText,
}: {
  items?: string[];
  emptyText: string;
}) {
  if (!items?.length) {
    return (
      <p className="text-sm text-[var(--text-muted)]">{emptyText}</p>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, index) => (
        <span
          key={`${item}-${index}`}
          className="rounded-lg border border-[var(--primary)]/10 bg-[var(--primary)]/[0.055] px-3 py-1.5 text-sm font-medium text-[var(--text-primary)] transition-colors hover:bg-[var(--primary)]/[0.10]"
        >
          {item}
        </span>
      ))}
    </div>
  );
}

function InfoBlock({
  label,
  value,
  emptyText,
}: {
  label: string;
  value?: string | null;
  emptyText: string;
}) {
  return (
    <div className="rounded-xl border border-[var(--border)]/70 bg-[var(--background)] p-4">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
        {label}
      </p>

      <p className="whitespace-pre-wrap break-words text-sm leading-6 text-[var(--text-secondary)]">
        {value?.trim() || emptyText}
      </p>
    </div>
  );
}

export default function MemoryPage() {
  const {
    profile,
    isLoading,
    error,
    refetch,
  } = useProfile();

  const isError = !!error;
  const isFetching = isLoading;

  if (isLoading) {
    return (
      <main className="min-h-screen bg-[var(--background)] px-4 py-8 sm:px-8">
        <div className="mx-auto max-w-6xl animate-pulse space-y-6">
          <div className="space-y-3">
            <div className="h-3 w-32 rounded bg-[var(--border)]" />
            <div className="h-9 w-48 rounded-lg bg-[var(--border)]" />
          </div>

          <div className="h-44 rounded-2xl bg-[var(--surface)]" />

          <div className="grid gap-5 md:grid-cols-2">
            {Array.from({ length: 4 }).map((_, index) => (
              <div
                key={index}
                className="h-64 rounded-2xl bg-[var(--surface)]"
              />
            ))}
          </div>
        </div>
      </main>
    );
  }

  if (isError || !profile) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4 py-12 sm:px-8">
        <div className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center shadow-sm">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/10 text-red-600">
            <AlertCircle size={23} />
          </div>

          <h1 className="mt-4 text-xl font-semibold text-[var(--text-primary)]">
            Couldn't load your memory
          </h1>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            We couldn't retrieve your saved profile information.
            Please try again.
          </p>

          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching}
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:opacity-60"
          >
            <RefreshCw
              size={15}
              className={isFetching ? "animate-spin" : ""}
            />
            Try again
          </button>
        </div>
      </main>
    );
  }

  const education = profile.education;
  const career = profile.career_goals;
  const skills = profile.skills;
  const preferences = profile.preferences;
  const directives = profile.explicit_directives ?? [];

  return (
    <main className="min-h-screen bg-[var(--background)] px-4 py-7 sm:px-8 sm:py-10">
      <div className="mx-auto max-w-6xl space-y-7">

        {/* Page heading */}
        <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-lg border border-[var(--primary)]/10 bg-[var(--primary)]/[0.06] px-3 py-1.5 text-xs font-semibold tracking-wide text-[var(--primary)]">
              <Brain size={15} />
              PERSONAL CONTEXT
            </div>

            <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)] sm:text-4xl">
              Memory
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
              Your learning profile, career goals, skills, and saved
              instructions — organized in one place.
            </p>
          </div>

          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching}
            className="inline-flex w-fit items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2.5 text-sm font-medium text-[var(--text-primary)] transition hover:border-[var(--primary)]/30 hover:bg-[var(--primary)]/[0.04] disabled:opacity-60"
          >
            <RefreshCw
              size={15}
              className={isFetching ? "animate-spin" : ""}
            />
            Refresh
          </button>
        </header>

        {/* Profile overview */}
        <section className="relative overflow-hidden rounded-2xl border border-[var(--primary)]/15 bg-[var(--primary)]/[0.075] p-5 sm:p-7">
          <div className="pointer-events-none absolute -right-12 -top-16 h-52 w-52 rounded-full border-[30px] border-[var(--primary)]/[0.045]" />

          <div className="pointer-events-none absolute -bottom-20 right-36 h-44 w-44 rounded-full bg-[var(--primary)]/[0.035]" />

          <div className="relative flex flex-col gap-5 sm:flex-row sm:items-center">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-[var(--primary)]/15 bg-[var(--surface)] text-[var(--primary)] shadow-sm">
              <UserRound size={26} strokeWidth={1.7} />
            </div>

            <div className="min-w-0 flex-1">
              <div className="mb-1.5 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--primary)]">
                <Sparkles size={14} />
                Learning identity
              </div>

              <h2 className="break-words text-xl font-bold tracking-tight text-[var(--text-primary)] sm:text-2xl">
                {career?.primary_goal || "Your learning profile"}
              </h2>

              <p className="mt-1.5 text-sm text-[var(--text-secondary)]">
                {education?.university || "University not provided"}
                {education?.degree_program
                  ? ` · ${education.degree_program}`
                  : ""}
              </p>
            </div>

            <div className="hidden shrink-0 items-center gap-1.5 rounded-full border border-[var(--primary)]/15 bg-[var(--surface)] px-3 py-2 text-xs font-medium text-[var(--primary)] sm:flex">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--primary)]" />
              Profile overview
            </div>
          </div>

          <div className="relative mt-6 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-[var(--primary)]/10 bg-[var(--surface)]/80 p-4">
              <p className="text-xs font-medium text-[var(--text-muted)]">
                Learning depth
              </p>
              <p className="mt-1.5 text-sm font-semibold text-[var(--text-primary)]">
                {preferences?.learning_depth || "Not set"}
              </p>
            </div>

            <div className="rounded-xl border border-[var(--primary)]/10 bg-[var(--surface)]/80 p-4">
              <p className="text-xs font-medium text-[var(--text-muted)]">
                Daily study hours
              </p>
              <p className="mt-1.5 text-sm font-semibold text-[var(--text-primary)]">
                {preferences?.daily_study_hours || "Not set"}
              </p>
            </div>

            <div className="rounded-xl border border-[var(--primary)]/10 bg-[var(--surface)]/80 p-4">
              <p className="text-xs font-medium text-[var(--text-muted)]">
                Saved directives
              </p>
              <p className="mt-1.5 text-sm font-semibold text-[var(--text-primary)]">
                {directives.length}{" "}
                {directives.length === 1 ? "instruction" : "instructions"}
              </p>
            </div>
          </div>
        </section>

        {/* Main information */}
        <div className="grid items-start gap-5 md:grid-cols-2">

          {/* Education */}
          <SectionCard
            title="Education"
            description="Your academic background"
            icon={GraduationCap}
          >
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <Detail label="University" value={education?.university} />

              <Detail
                label="Degree / Program"
                value={education?.degree_program || education?.degree}
              />

              <Detail
                label="Academic status"
                value={education?.academic_status}
              />

              <Detail
                label="Current year"
                value={education?.current_year}
              />

              <Detail label="Domain" value={education?.domain} />

              <Detail
                label="Graduation year"
                value={education?.graduation_year}
              />
            </div>

            <div className="mt-5">
              <p className="mb-3 text-sm font-semibold text-[var(--text-primary)]">
                Subjects
              </p>

              <TagList
                items={education?.subjects}
                emptyText="No subjects added yet."
              />
            </div>
          </SectionCard>

          {/* Career */}
          <SectionCard
            title="Career goals"
            description="What you're working towards"
            icon={Target}
          >
            <div className="rounded-xl border border-[var(--border)]/70 bg-[var(--background)] p-4">
              <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                Primary goal
              </p>

              <p className="break-words text-base font-semibold text-[var(--text-primary)]">
                {career?.primary_goal || "Not provided"}
              </p>
            </div>

            <div className="mt-5">
              <p className="mb-3 text-sm font-semibold text-[var(--text-primary)]">
                Target skills
              </p>

              <TagList
                items={career?.target_skills}
                emptyText="No target skills added yet."
              />
            </div>
          </SectionCard>

          {/* Skills and experience */}
          <SectionCard
            title="Skills & experience"
            description="Your existing knowledge and work"
            icon={BriefcaseBusiness}
          >
            <div>
              <p className="mb-3 text-sm font-semibold text-[var(--text-primary)]">
                Skills
              </p>

              <TagList
                items={skills?.skills}
                emptyText="No skills added yet."
              />
            </div>

            <div className="mt-5">
              <p className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--text-primary)]">
                <FolderKanban size={16} className="text-[var(--primary)]" />
                Projects
              </p>

              <TagList
                items={skills?.projects}
                emptyText="No projects added yet."
              />
            </div>

            <div className="mt-5 space-y-3">
              <InfoBlock
                label="Research"
                value={skills?.research}
                emptyText="No research information provided."
              />

              <InfoBlock
                label="Experience"
                value={skills?.experience}
                emptyText="No experience information provided."
              />
            </div>
          </SectionCard>

          {/* Learning preferences */}
          <SectionCard
            title="Learning preferences"
            description="How you prefer to study"
            icon={BookOpen}
          >
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <Detail
                label="Daily study hours"
                value={preferences?.daily_study_hours}
              />

              <Detail
                label="Learning depth"
                value={preferences?.learning_depth}
              />
            </div>

            <div className="mt-5 rounded-xl border border-[var(--primary)]/10 bg-[var(--primary)]/[0.045] p-4">
              <div className="flex items-start gap-3">
                <Clock3
                  size={19}
                  className="mt-0.5 shrink-0 text-[var(--primary)]"
                />

                <div>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    Personalized learning
                  </p>

                  <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                    These preferences help tailor your learning
                    experience around your available time and preferred
                    depth of study.
                  </p>
                </div>
              </div>
            </div>
          </SectionCard>
        </div>

        {/* Saved instructions */}
        <SectionCard
          title="Saved instructions"
          description="Explicit directives saved for your personalized experience"
          icon={Lightbulb}
        >
          {directives.length > 0 ? (
            <div className="grid gap-3 sm:grid-cols-2">
              {directives.map((directive, index) => (
                <div
                  key={`${directive}-${index}`}
                  className="flex min-w-0 items-start gap-3 rounded-xl border border-[var(--border)] bg-[var(--background)] p-4 transition-colors hover:border-[var(--primary)]/25"
                >
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--primary)]/[0.07] text-[var(--primary)]">
                    <Lightbulb size={16} />
                  </div>

                  <p className="min-w-0 whitespace-pre-wrap break-words text-sm leading-6 text-[var(--text-primary)]">
                    {directive}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-[var(--border)] px-5 py-9 text-center">
              <Lightbulb
                size={24}
                className="mx-auto mb-3 text-[var(--text-muted)]"
              />

              <p className="text-sm font-semibold text-[var(--text-primary)]">
                No saved instructions yet
              </p>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                Your explicit directives will appear here when available.
              </p>
            </div>
          )}
        </SectionCard>

        {/* Footer */}
        <footer className="flex items-center justify-center gap-2 border-t border-[var(--border)] pt-5 pb-3 text-xs text-[var(--text-muted)]">
          <Brain size={14} />
          Your saved learning context
          <ChevronRight size={13} />
          <span>Read only</span>
        </footer>
      </div>
    </main>
  );
}
