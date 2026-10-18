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

function formatDate(value?: string | null) {
  if (!value) return 'Not specified';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Not specified';
  return new Intl.DateTimeFormat(undefined, { day: 'numeric', month: 'short', year: 'numeric' }).format(date);
}

function typeLabel(type: CompetitionType) {
  return typeOptions.find((option) => option.value === type)?.label ?? 'Competition';
}

function statusLabel(status: CompetitionRecord['status']) {
  return status.replaceAll('_', ' ').toLowerCase().replace(/^\w/, (char) => char.toUpperCase());
}

function CompetitionCard({ item }: { item: CompetitionRecord }) {
  return (
    <article className="flex h-full flex-col rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 transition hover:-translate-y-0.5 hover:shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-[var(--primary-soft)] px-2.5 py-1 text-xs font-medium text-[var(--primary)]">
          {typeLabel(item.type)}
        </span>
        <span className="rounded-full border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--text-secondary)]">
          {statusLabel(item.status)}
        </span>
        {item.isRecommended ? (
          <span className="rounded-full bg-[#F3E8D5] px-2.5 py-1 text-xs font-medium text-[#765526]">
            Recommended
          </span>
        ) : null}
      </div>

      <h2 className="mt-4 text-lg font-semibold leading-snug text-[var(--text-primary)]">{item.title}</h2>
      <p className="mt-2 line-clamp-3 text-sm leading-6 text-[var(--text-secondary)]">{item.summary}</p>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {(item.domains?.length ? item.domains : [item.domain]).map((domain) => (
          <span key={domain} className="rounded-md bg-[var(--surface-alt)] px-2 py-1 text-xs text-[var(--text-label)]">
            {domain.replaceAll('_', ' ')}
          </span>
        ))}
        <span className="rounded-md bg-[var(--surface-alt)] px-2 py-1 text-xs text-[var(--text-label)]">
          {item.difficulty.replaceAll('_', ' ')}
        </span>
      </div>

      <div className="mt-5 space-y-2 text-sm">
        <p className="text-[var(--text-secondary)]">
          <span className="font-medium text-[var(--text-primary)]">Organizer:</span> {item.organizer.name}
        </p>
        <p className="text-[var(--text-secondary)]">
          <span className="font-medium text-[var(--text-primary)]">Deadline:</span> {formatDate(item.deadlineAt)}
        </p>
        <p className="text-[var(--text-secondary)]">
          <span className="font-medium text-[var(--text-primary)]">Eligibility:</span> {item.eligibility.summary}
        </p>
      </div>

      {item.skills.length ? (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {item.skills.slice(0, 5).map((skill) => (
            <span key={skill} className="rounded-full border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--text-secondary)]">
              {skill}
            </span>
          ))}
        </div>
      ) : null}

      <div className="mt-auto flex flex-wrap gap-3 pt-6">
        <Link
          href={`/compete/${encodeURIComponent(item.id)}`}
          className="inline-flex items-center justify-center rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[var(--primary-hover)]"
        >
          View details
        </Link>
        <a
          href={item.registrationUrl}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center justify-center rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-alt)]"
        >
          Register ↗
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
    difficulty: difficulty ? [difficulty as NonNullable<CompetitionFilters['difficulty']>[number]] : undefined,
    status: status ? [status as NonNullable<CompetitionFilters['status']>[number]] : undefined,
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

  return (
    <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--text-secondary)]">Discover • Prepare • Participate</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-[var(--text-primary)]">Compete</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
            Find hackathons, coding competitions, and student challenges that fit your skills, goals, and eligibility.
          </p>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--text-secondary)]">
          Opportunities from one universal competition feed
        </div>
      </div>

      <section aria-label="Competition filters" className="mt-7 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 sm:p-5">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-6">
          <label className="lg:col-span-2">
            <span className="mb-1.5 block text-xs font-semibold text-[var(--text-label)]">Search</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Title, organizer, skill…"
              className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--primary)]"
            />
          </label>
          <label>
            <span className="mb-1.5 block text-xs font-semibold text-[var(--text-label)]">Type</span>
            <select value={type} onChange={(event) => setType(event.target.value)} className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2.5 text-sm">
              <option value="">All types</option>
              {typeOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
          <label>
            <span className="mb-1.5 block text-xs font-semibold text-[var(--text-label)]">Domain</span>
            <select value={domain} onChange={(event) => setDomain(event.target.value)} className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2.5 text-sm">
              <option value="">All domains</option>
              {domainOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
          <label>
            <span className="mb-1.5 block text-xs font-semibold text-[var(--text-label)]">Difficulty</span>
            <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)} className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2.5 text-sm">
              <option value="">Any level</option>
              {difficultyOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
          <label>
            <span className="mb-1.5 block text-xs font-semibold text-[var(--text-label)]">Status</span>
            <select value={status} onChange={(event) => setStatus(event.target.value)} className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2.5 text-sm">
              <option value="">All statuses</option>
              <option value="OPEN">Open</option>
              <option value="CLOSING_SOON">Closing soon</option>
              <option value="UPCOMING">Upcoming</option>
              <option value="ONGOING">Ongoing</option>
              <option value="CLOSED">Closed</option>
            </select>
          </label>
          <label>
            <span className="mb-1.5 block text-xs font-semibold text-[var(--text-label)]">Sort by</span>
            <select value={sort} onChange={(event) => setSort(event.target.value as CompetitionFilters['sort'])} className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2.5 text-sm">
              <option value="deadline_asc">Closest deadline</option>
              <option value="recommended">Recommended</option>
              <option value="newest">Newest</option>
            </select>
          </label>
          <div className="flex items-end">
            <button type="button" onClick={resetFilters} className="w-full rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-alt)]">
              Reset filters
            </button>
          </div>
        </div>
      </section>

      <div className="mt-6 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Available opportunities</h2>
        {competitions.data ? (
          <span className="text-sm text-[var(--text-secondary)]">{competitions.data.total} results</span>
        ) : null}
      </div>

      <div className="mt-4">
        {competitions.isPending ? (
          <CompeteLoadingState />
        ) : competitions.isError ? (
          <CompeteErrorState
            message={competitions.error instanceof Error ? competitions.error.message : undefined}
            onRetry={() => void competitions.refetch()}
          />
        ) : competitions.data.items.length === 0 ? (
          <CompeteEmptyState action={<button type="button" onClick={resetFilters} className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white">Clear filters</button>} />
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {competitions.data.items.map((item) => <CompetitionCard key={item.id} item={item} />)}
          </div>
        )}
      </div>
    </main>
  );
}
