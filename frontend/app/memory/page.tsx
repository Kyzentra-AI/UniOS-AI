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
    <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      <div className="mb-5 flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--primary-soft)] text-[var(--primary)]">
          <Icon size={20} />
        </div>

        <div>
          <h2 className="text-base font-semibold text-[var(--text-primary)]">
            {title}
          </h2>
          {description && (
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
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
    <div className="min-w-0 rounded-xl bg-[var(--background)] p-3.5">
      <p className="mb-1 text-xs font-medium text-[var(--text-secondary)]">
        {label}
      </p>
      <p className="break-words text-sm font-medium text-[var(--text-primary)]">
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
      <p className="text-sm text-[var(--text-secondary)]">{emptyText}</p>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, index) => (
        <span
          key={`${item}-${index}`}
          className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-sm text-[var(--text-primary)]"
        >
          {item}
        </span>
      ))}
    </div>
  );
}

export default function MemoryPage() {
  const { data: profile, isLoading, isError, refetch, isFetching } =
    useProfile();

  if (isLoading) {
    return (
      <main className="min-h-screen bg-[var(--background)] px-4 py-8 sm:px-8">
        <div className="mx-auto max-w-6xl animate-pulse space-y-6">
          <div className="h-8 w-48 rounded-lg bg-[var(--border)]" />
          <div className="h-36 rounded-2xl bg-[var(--surface)]" />
          <div className="grid gap-5 md:grid-cols-2">
            <div className="h-56 rounded-2xl bg-[var(--surface)]" />
            <div className="h-56 rounded-2xl bg-[var(--surface)]" />
          </div>
        </div>
      </main>
    );
  }

  if (isError || !profile) {
    return (
      <main className="min-h-screen bg-[var(--background)] px-4 py-12 sm:px-8">
        <div className="mx-auto max-w-xl rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center">
          <AlertCircle
            className="mx-auto mb-4 text-[var(--danger-text)]"
            size={36}
          />

          <h1 className="text-xl font-semibold text-[var(--text-primary)]">
            Couldn't load your memory
          </h1>

          <p className="mt-2 text-sm text-[var(--text-secondary)]">
            We couldn't retrieve your saved profile information. Please try
            again.
          </p>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[var(--primary-hover)] disabled:opacity-60"
          >
            <RefreshCw size={16} className={isFetching ? "animate-spin" : ""} />
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
        <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm font-medium text-[var(--primary)]">
              <Brain size={17} />
              Your personal context
            </div>

            <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)] sm:text-4xl">
              Memory
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
              Your learning profile, career goals, skills, and saved
              instructions in one place.
            </p>
          </div>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="inline-flex w-fit items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2.5 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--primary-soft)] disabled:opacity-60"
          >
            <RefreshCw
              size={15}
              className={isFetching ? "animate-spin" : ""}
            />
            Refresh
          </button>
        </header>

        {/* Profile overview */}
        <section className="relative overflow-hidden rounded-2xl bg-[var(--primary)] p-6 text-white sm:p-8">
          <div className="pointer-events-none absolute -right-10 -top-16 h-48 w-48 rounded-full border-[28px] border-white/5" />
          <div className="pointer-events-none absolute -bottom-20 right-24 h-40 w-40 rounded-full bg-white/5" />

          <div className="relative flex items-start gap-4 sm:items-center sm:gap-5">
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl border border-white/20 bg-white/10">
              <UserRound size={30} />
            </div>

            <div className="min-w-0">
              <div className="mb-1 flex items-center gap-2 text-sm text-white/75">
                <Sparkles size={15} />
                Your learning identity
              </div>

              <h2 className="text-xl font-semibold sm:text-2xl">
                {career?.primary_goal || "Your learning profile"}
              </h2>

              <p className="mt-1 text-sm text-white/75">
                {education?.university || "University not provided"}
                {education?.degree_program
                  ? ` · ${education.degree_program}`
                  : ""}
              </p>
            </div>
          </div>

          <div className="relative mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-white/10 p-4">
              <p className="text-sm text-white/70">Learning depth</p>
              <p className="mt-1 font-semibold">
                {preferences?.learning_depth || "Not set"}
              </p>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/10 p-4">
              <p className="text-sm text-white/70">Daily study hours</p>
              <p className="mt-1 font-semibold">
                {preferences?.daily_study_hours || "Not set"}
              </p>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/10 p-4">
              <p className="text-sm text-white/70">Saved directives</p>
              <p className="mt-1 font-semibold">
                {directives.length}{" "}
                {directives.length === 1 ? "instruction" : "instructions"}
              </p>
            </div>
          </div>
        </section>

        {/* Main information */}
        <div className="grid gap-5 md:grid-cols-2">
          <SectionCard
            title="Education"
            description="Your academic background"
            icon={GraduationCap}
          >
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <Detail
                label="University"
                value={education?.university}
              />
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
              <Detail
                label="Domain"
                value={education?.domain}
              />
              <Detail
                label="Graduation year"
                value={education?.graduation_year}
              />
            </div>

            <div className="mt-5">
              <p className="mb-3 text-sm font-medium text-[var(--text-primary)]">
                Subjects
              </p>
              <TagList
                items={education?.subjects}
                emptyText="No subjects added yet."
              />
            </div>
          </SectionCard>

          <SectionCard
            title="Career goals"
            description="What you're working towards"
            icon={Target}
          >
            <div className="rounded-xl bg-[var(--background)] p-4">
              <p className="mb-1 text-xs font-medium text-[var(--text-secondary)]">
                Primary goal
              </p>
              <p className="text-base font-semibold text-[var(--text-primary)]">
                {career?.primary_goal || "Not provided"}
              </p>
            </div>

            <div className="mt-5">
              <p className="mb-3 text-sm font-medium text-[var(--text-primary)]">
                Target skills
              </p>
              <TagList
                items={career?.target_skills}
                emptyText="No target skills added yet."
              />
            </div>
          </SectionCard>

          <SectionCard
            title="Skills & experience"
            description="Your existing experience and work"
            icon={BriefcaseBusiness}
          >
            <div>
              <p className="mb-3 text-sm font-medium text-[var(--text-primary)]">
                Skills
              </p>
              <TagList
                items={skills?.skills}
                emptyText="No skills added yet."
              />
            </div>

            <div className="mt-5">
              <p className="mb-3 flex items-center gap-2 text-sm font-medium text-[var(--text-primary)]">
                <FolderKanban size={16} />
                Projects
              </p>
              <TagList
                items={skills?.projects}
                emptyText="No projects added yet."
              />
            </div>

            <div className="mt-5 grid gap-3">
              <div className="rounded-xl bg-[var(--background)] p-4">
                <p className="mb-1 text-xs font-medium text-[var(--text-secondary)]">
                  Research
                </p>
                <p className="whitespace-pre-wrap break-words text-sm text-[var(--text-primary)]">
                  {skills?.research || "No research information provided."}
                </p>
              </div>

              <div className="rounded-xl bg-[var(--background)] p-4">
                <p className="mb-1 text-xs font-medium text-[var(--text-secondary)]">
                  Experience
                </p>
                <p className="whitespace-pre-wrap break-words text-sm text-[var(--text-primary)]">
                  {skills?.experience || "No experience information provided."}
                </p>
              </div>
            </div>
          </SectionCard>

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

            <div className="mt-5 rounded-xl border border-[var(--border)] bg-[var(--background)] p-4">
              <div className="flex items-start gap-3">
                <Clock3
                  size={19}
                  className="mt-0.5 shrink-0 text-[var(--primary)]"
                />
                <div>
                  <p className="text-sm font-medium text-[var(--text-primary)]">
                    Personalized learning
                  </p>
                  <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                    These preferences help tailor your learning experience
                    around your available time and preferred depth of study.
                  </p>
                </div>
              </div>
            </div>
          </SectionCard>
        </div>

        {/* Saved memory / directives */}
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
                  className="flex items-start gap-3 rounded-xl border border-[var(--border)] bg-[var(--background)] p-4"
                >
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--primary-soft)] text-[var(--primary)]">
                    <Lightbulb size={16} />
                  </div>

                  <p className="whitespace-pre-wrap break-words text-sm leading-6 text-[var(--text-primary)]">
                    {directive}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-[var(--border)] px-5 py-8 text-center">
              <Lightbulb
                size={26}
                className="mx-auto mb-3 text-[var(--text-secondary)]"
              />
              <p className="font-medium text-[var(--text-primary)]">
                No saved instructions yet
              </p>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                Your explicit directives will appear here when available.
              </p>
            </div>
          )}
        </SectionCard>

        <p className="pb-4 text-center text-xs text-[var(--text-secondary)]">
          This page displays your saved information. Editing is not available
          here.
        </p>
      </div>
    </main>
  );
}