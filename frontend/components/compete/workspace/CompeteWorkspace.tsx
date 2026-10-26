
'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useCompetitions } from '@/hooks/useCompete';
import type {
  CompetitionDomain,
  CompetitionFilters,
  CompetitionRecord,
  CompetitionType,
} from '@/types/compete';
import {
  CompeteEmptyState,
  CompeteErrorState,
  CompeteLoadingState,
} from '@/components/compete/states/CompeteStates';
import { Chevron, stagger } from '@/components/roadmap/UI';

const typeOptions: { value: CompetitionType; label: string }[] = [
  { value: 'HACKATHON', label: 'Hackathons' },
  { value: 'CODING_COMPETITION', label: 'Coding competitions' },
  { value: 'INNOVATION_CHALLENGE', label: 'Innovation challenges' },
  { value: 'STUDENT_CHALLENGE', label: 'Student challenges' },
  { value: 'CASE_COMPETITION', label: 'Case competitions' },
  { value: 'RESEARCH_CHALLENGE', label: 'Research challenges' },
  { value: 'OTHER', label: 'Other' },
];

const domainOptions: { value: CompetitionDomain; label: string }[] = [
  { value: 'AI_ML', label: 'AI / ML' },
  { value: 'WEB_DEVELOPMENT', label: 'Web development' },
  { value: 'DATA_SCIENCE', label: 'Data science' },
  { value: 'CYBERSECURITY', label: 'Cybersecurity' },
  { value: 'CLOUD_DEVOPS', label: 'Cloud / DevOps' },
  { value: 'DESIGN', label: 'Design' },
  { value: 'BUSINESS', label: 'Business' },
  { value: 'ROBOTICS', label: 'Robotics' },
  { value: 'SUSTAINABILITY', label: 'Sustainability' },
  { value: 'GENERAL', label: 'General' },
];

const difficultyOptions = [
  { value: 'BEGINNER', label: 'Beginner' },
  { value: 'INTERMEDIATE', label: 'Intermediate' },
  { value: 'ADVANCED', label: 'Advanced' },
  { value: 'ALL_LEVELS', label: 'All levels' },
] as const;

const statusOptions = [
  { value: '', label: 'All statuses' },
  { value: 'OPEN', label: 'Open' },
  { value: 'CLOSING_SOON', label: 'Closing soon' },
  { value: 'UPCOMING', label: 'Upcoming' },
  { value: 'ONGOING', label: 'Ongoing' },
  { value: 'CLOSED', label: 'Closed' },
];

function formatDate(value?: string | null) {
  if (!value) return 'Not specified';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Not specified';

  return new Intl.DateTimeFormat(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

function typeLabel(type: CompetitionType) {
  return typeOptions.find((option) => option.value === type)?.label ?? 'Competition';
}

function statusLabel(status: CompetitionRecord['status']) {
  return status.replaceAll('_', ' ').toLowerCase().replace(/^\w/, (char) => char.toUpperCase());
}

function deadlineInfo(value?: string | null) {
  if (!value) return null;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;

  const days = Math.ceil((date.getTime() - Date.now()) / 86400000);

  if (days < 0) {
    return { text: 'Deadline passed', bg: 'var(--surface-alt)', fg: 'var(--text-secondary)' };
  }
  if (days === 0) {
    return { text: 'Closes today', bg: 'var(--feature-orange-soft)', fg: 'var(--feature-orange)' };
  }
  if (days === 1) {
    return { text: 'Closes tomorrow', bg: 'var(--feature-orange-soft)', fg: 'var(--feature-orange)' };
  }

  return days <= 3
    ? { text: `${days} days left`, bg: 'var(--feature-orange-soft)', fg: 'var(--feature-orange)' }
    : { text: `${days} days left`, bg: 'var(--primary-soft)', fg: 'var(--primary)' };
}

const statusTone = (status: string) =>
  status === 'OPEN'
    ? { bg: 'var(--primary-soft)', fg: 'var(--primary)' }
    : status === 'CLOSING_SOON'
      ? { bg: 'var(--feature-orange-soft)', fg: 'var(--feature-orange)' }
      : status === 'UPCOMING' || status === 'ONGOING'
        ? { bg: 'var(--feature-blue-soft)', fg: 'var(--feature-blue)' }
        : { bg: 'var(--surface-alt)', fg: 'var(--text-secondary)' };

function External({ className = '' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={`h-3.5 w-3.5 ${className}`}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M6.5 3.5H4a1 1 0 0 0-1 1V12a1 1 0 0 0 1 1h7.5a1 1 0 0 0 1-1V9.5M9.5 3h3.5v3.5M13 3 7.5 8.5" />
    </svg>
  );
}

function CompetitionCard({ item }: { item: CompetitionRecord }) {
  const tone = statusTone(item.status);
  const deadline = deadlineInfo(item.deadlineAt);

  return (
    <article className="group flex h-full flex-col rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_14px_34px_rgba(24,52,58,0.08)]">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-[var(--primary-soft)] px-2.5 py-1 text-xs font-medium text-[var(--primary)]">
          {typeLabel(item.type)}
        </span>

        <span
          className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
          style={{ backgroundColor: tone.bg, color: tone.fg }}
        >
          <span className="h-1.5 w-1.5 rounded-full bg-current" />
          {statusLabel(item.status)}
        </span>

        {item.isRecommended ? (
          <span className="rounded-full bg-[#F3E8D5] px-2.5 py-1 text-xs font-medium text-[#765526]">
            Recommended
          </span>
        ) : null}
      </div>

      <h2 className="mt-4 text-lg font-semibold leading-snug text-[var(--text-primary)]">
        {item.title}
      </h2>

      <p className="mt-2 line-clamp-3 text-sm leading-6 text-[var(--text-secondary)]">
        {item.summary}
      </p>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {(item.domains?.length ? item.domains : [item.domain]).map((domain) => (
          <span
            key={domain}
            className="rounded-lg bg-[var(--surface-alt)] px-2 py-1 text-xs text-[var(--text-label)]"
          >
            {domain.replaceAll('_', ' ')}
          </span>
        ))}

        <span className="rounded-lg bg-[var(--surface-alt)] px-2 py-1 text-xs text-[var(--text-label)]">
          {item.difficulty.replaceAll('_', ' ')}
        </span>
      </div>

      <dl className="mt-5 space-y-2.5 border-t border-[var(--border)] pt-4 text-sm">
        <div className="flex gap-3">
          <dt className="w-20 shrink-0 text-[var(--text-muted)]">Organizer</dt>
          <dd className="min-w-0 font-medium text-[var(--text-primary)]">
            {item.organizer.name}
          </dd>
        </div>

        <div className="flex gap-3">
          <dt className="w-20 shrink-0 text-[var(--text-muted)]">Deadline</dt>
          <dd className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
            <span className="font-medium text-[var(--text-primary)]">
              {formatDate(item.deadlineAt)}
            </span>

            {deadline && (
              <span
                className="rounded-full px-2 py-0.5 text-xs font-medium"
                style={{ backgroundColor: deadline.bg, color: deadline.fg }}
              >
                {deadline.text}
              </span>
            )}
          </dd>
        </div>

        <div className="flex gap-3">
          <dt className="w-20 shrink-0 text-[var(--text-muted)]">Eligibility</dt>
          <dd className="line-clamp-2 min-w-0 text-[var(--text-secondary)]">
            {item.eligibility.summary}
          </dd>
        </div>
      </dl>

      {item.skills.length ? (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {item.skills.slice(0, 5).map((skill) => (
            <span
              key={skill}
              className="rounded-full border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--text-secondary)]"
            >
              {skill}
            </span>
          ))}
        </div>
      ) : null}

      <div className="mt-auto flex flex-wrap gap-2.5 pt-6">
        <Link
          href={`/compete/${encodeURIComponent(item.id)}`}
          className="inline-flex flex-1 items-center justify-center gap-1 rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2 sm:flex-none"
        >
          View details
          <Chevron className="transition-transform duration-200 group-hover:translate-x-0.5" />
        </Link>

        <a
          href={item.registrationUrl}
          target="_blank"
          rel="noreferrer"
          className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] sm:flex-none"
        >
          Register
          <External />
        </a>
      </div>
    </article>
  );
}

export default function CompeteWorkspace() {
  const [search, setSearch] = useState('');
  const [type, setType] = useState('');
  const [domain, setDomain] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [status, setStatus] = useState('OPEN');
  const [sort, setSort] = useState<CompetitionFilters['sort']>('deadline_asc');

  const filters = useMemo<CompetitionFilters>(() => ({
    search: search.trim() || undefined,
    types: type ? [type as CompetitionType] : undefined,
    domains: domain ? [domain as CompetitionDomain] : undefined,
    difficulty: difficulty
      ? [difficulty as NonNullable<CompetitionFilters['difficulty']>[number]]
      : undefined,
    status: status
      ? [status as NonNullable<CompetitionFilters['status']>[number]]
      : undefined,
    sort,
    page: 1,
    pageSize: 24,
  }), [search, type, domain, difficulty, status, sort]);

  const competitions = useCompetitions(filters);

  function resetFilters() {
    setSearch('');
    setType('');
    setDomain('');
    setDifficulty('');
    setStatus('');
    setSort('deadline_asc');
  }

  const nothingToReset =
    !search && !type && !domain && !difficulty && !status && sort === 'deadline_asc';

  return (
    <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <header className="rise">
        <h1 className="text-[28px] font-bold leading-tight tracking-tight text-[var(--text-primary)] sm:text-4xl">
          Compete
        </h1>
        <p className="mt-2 max-w-2xl text-[15px] leading-6 text-[var(--text-secondary)]">
          Find hackathons, coding competitions, and student challenges that fit your skills, goals, and eligibility.
        </p>
      </header>

      {/* Compact filters */}
      <section
        aria-label="Competition filters"
        className="rise mt-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-3 shadow-[0_6px_20px_rgba(24,52,58,0.04)] sm:p-4"
        style={stagger(1)}
      >
        <div className="relative">
          <svg
            viewBox="0 0 16 16"
            className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <circle cx="7" cy="7" r="4.5" />
            <path d="m10.5 10.5 3 3" />
          </svg>

          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            aria-label="Search competitions"
            placeholder="Search competitions, organizers or skills..."
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] py-2.5 pl-10 pr-10 text-sm text-[var(--text-primary)] outline-none transition placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:shadow-[0_0_0_3px_var(--primary-soft)]"
          />

          {search && (
            <button
              type="button"
              aria-label="Clear search"
              onClick={() => setSearch('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded-full p-1.5 text-[var(--text-muted)] transition hover:bg-[var(--surface-alt)] hover:text-[var(--text-primary)]"
            >
              <svg
                viewBox="0 0 16 16"
                className="h-3.5 w-3.5"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                aria-hidden="true"
              >
                <path d="M4 4l8 8M12 4l-8 8" />
              </svg>
            </button>
          )}
        </div>

        <div className="mt-3 flex items-center gap-2 overflow-x-auto pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          <div className="relative min-w-[125px] flex-1">
            <select
              aria-label="Filter by status"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              className="w-full appearance-none rounded-xl border border-[var(--border)] bg-[var(--background)] py-2.5 pl-3 pr-8 text-sm font-medium text-[var(--text-primary)] outline-none transition hover:border-[var(--primary)] focus:border-[var(--primary)] focus:shadow-[0_0_0_3px_var(--primary-soft)]"
            >
              {statusOptions.map((option) => (
                <option key={option.value || 'all'} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <Chevron className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rotate-90 text-[var(--text-muted)]" />
          </div>

          <div className="relative min-w-[145px] flex-1">
            <select
              aria-label="Filter by competition type"
              value={type}
              onChange={(event) => setType(event.target.value)}
              className="w-full appearance-none rounded-xl border border-[var(--border)] bg-[var(--background)] py-2.5 pl-3 pr-8 text-sm font-medium text-[var(--text-primary)] outline-none transition hover:border-[var(--primary)] focus:border-[var(--primary)] focus:shadow-[0_0_0_3px_var(--primary-soft)]"
            >
              <option value="">All types</option>
              {typeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <Chevron className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rotate-90 text-[var(--text-muted)]" />
          </div>

          <div className="relative min-w-[130px] flex-1">
            <select
              aria-label="Filter by domain"
              value={domain}
              onChange={(event) => setDomain(event.target.value)}
              className="w-full appearance-none rounded-xl border border-[var(--border)] bg-[var(--background)] py-2.5 pl-3 pr-8 text-sm font-medium text-[var(--text-primary)] outline-none transition hover:border-[var(--primary)] focus:border-[var(--primary)] focus:shadow-[0_0_0_3px_var(--primary-soft)]"
            >
              <option value="">All domains</option>
              {domainOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <Chevron className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rotate-90 text-[var(--text-muted)]" />
          </div>

          <div className="relative min-w-[125px] flex-1">
            <select
              aria-label="Filter by difficulty"
              value={difficulty}
              onChange={(event) => setDifficulty(event.target.value)}
              className="w-full appearance-none rounded-xl border border-[var(--border)] bg-[var(--background)] py-2.5 pl-3 pr-8 text-sm font-medium text-[var(--text-primary)] outline-none transition hover:border-[var(--primary)] focus:border-[var(--primary)] focus:shadow-[0_0_0_3px_var(--primary-soft)]"
            >
              <option value="">Any level</option>
              {difficultyOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <Chevron className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rotate-90 text-[var(--text-muted)]" />
          </div>

          <button
            type="button"
            onClick={resetFilters}
            disabled={nothingToReset}
            className="shrink-0 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm font-medium text-[var(--primary)] transition hover:border-[var(--primary)] hover:bg-[var(--primary-soft)] disabled:cursor-not-allowed disabled:opacity-40"
          >
            Reset
          </button>
        </div>
      </section>

      <div className="mt-8 flex flex-wrap items-end justify-between gap-x-4 gap-y-3">
        <div className="min-w-0">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">
            Available opportunities
          </h2>
          <p className="mt-0.5 text-sm text-[var(--text-secondary)]" aria-live="polite">
            {competitions.data ? `${competitions.data.total} results` : 'Searching…'}
          </p>
        </div>

        <label className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
          Sort by
          <span className="relative block">
            <select
              value={sort}
              onChange={(event) => setSort(event.target.value as CompetitionFilters['sort'])}
              className="appearance-none rounded-xl border border-[var(--border)] bg-[var(--surface)] py-2 pl-3 pr-8 text-sm font-medium text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]"
            >
              <option value="deadline_asc">Closest deadline</option>
              <option value="recommended">Recommended</option>
              <option value="newest">Newest</option>
            </select>
            <Chevron className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rotate-90 text-[var(--text-muted)]" />
          </span>
        </label>
      </div>

      <div className="mt-4">
        {competitions.isPending ? (
          <CompeteLoadingState variant="grid" />
        ) : competitions.isError ? (
          <CompeteErrorState
            message={competitions.error instanceof Error ? competitions.error.message : undefined}
            onRetry={() => void competitions.refetch()}
          />
        ) : competitions.data.items.length === 0 ? (
          <CompeteEmptyState
            action={
              <button
                type="button"
                onClick={resetFilters}
                className="rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98]"
              >
                Clear filters
              </button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {competitions.data.items.map((item, i) => (
              <div key={item.id} className="rise" style={stagger(Math.min(i, 8))}>
                <CompetitionCard item={item} />
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
