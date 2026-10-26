'use client';

import Link from 'next/link';
import { useCompetition } from '@/hooks/useCompete';
import { CompeteEmptyState, CompeteErrorState, CompeteLoadingState } from '@/components/compete/states/CompeteStates';
import { Chevron, stagger } from '@/components/roadmap/UI';

function formatDate(value?: string | null) {
  if (!value) return 'Not specified';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Not specified';
  return new Intl.DateTimeFormat(undefined, {
    weekday: 'short',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

function deadlineInfo(value?: string | null) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  const days = Math.ceil((date.getTime() - Date.now()) / 86400000);
  if (days < 0) return { text: 'Deadline passed', bg: 'var(--surface-alt)', fg: 'var(--text-secondary)' };
  if (days === 0) return { text: 'Closes today', bg: 'var(--feature-orange-soft)', fg: 'var(--feature-orange)' };
  if (days === 1) return { text: 'Closes tomorrow', bg: 'var(--feature-orange-soft)', fg: 'var(--feature-orange)' };
  return days <= 3
    ? { text: `${days} days left`, bg: 'var(--feature-orange-soft)', fg: 'var(--feature-orange)' }
    : { text: `${days} days left`, bg: 'var(--primary-soft)', fg: 'var(--primary)' };
}

function External({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={`h-3.5 w-3.5 ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M6.5 3.5H4a1 1 0 0 0-1 1V12a1 1 0 0 0 1 1h7.5a1 1 0 0 0 1-1V9.5M9.5 3h3.5v3.5M13 3 7.5 8.5" />
    </svg>
  );
}

export default function CompetitionDetails({ competitionId }: { competitionId: string }) {
  const query = useCompetition(competitionId);

  if (query.isPending) return <main className="mx-auto max-w-5xl px-4 py-8"><CompeteLoadingState label="Loading competition details…" /></main>;
  if (query.isError) return <main className="mx-auto max-w-5xl px-4 py-8"><CompeteErrorState message={query.error instanceof Error ? query.error.message : undefined} onRetry={() => void query.refetch()} /></main>;
  if (!query.data?.competition) return <main className="mx-auto max-w-5xl px-4 py-8"><CompeteEmptyState title="Competition not found" description="This opportunity may have expired or been removed." /></main>;

  const item = query.data.competition;
  const deadline = deadlineInfo(item.deadlineAt);

  const glance: [string, string][] = [
    ['Organizer', item.organizer.name],
    ['Starts', formatDate(item.startsAt)],
    ['Ends', formatDate(item.endsAt)],
    ['Difficulty', item.difficulty.replaceAll('_', ' ')],
    ['Goal', item.goals.map((goal) => goal.replaceAll('_', ' ')).join(', ') || 'Not specified'],
    ...(item.prizeSummary ? [['Prize / benefits', item.prizeSummary] as [string, string]] : []),
    ['Team size', `${item.eligibility.minimumTeamSize ?? '—'}–${item.eligibility.maximumTeamSize ?? '—'} participants`],
  ];

  return (
    <main className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-8">
      <Link href="/compete" className="group inline-flex items-center gap-1 rounded-md py-1 text-sm font-semibold text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]">
        <Chevron className="rotate-180 transition-transform duration-200 group-hover:-translate-x-0.5" />
        Back to Compete
      </Link>

      <article className="rise mt-5 overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_28px_rgba(24,52,58,0.04)]">
        <div className="border-b border-[var(--border)] bg-[var(--surface-alt)] p-5 sm:p-8">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-[var(--primary-soft)] px-3 py-1 text-xs font-semibold text-[var(--primary)]">{item.type.replaceAll('_', ' ')}</span>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1 text-xs text-[var(--text-secondary)]">
              <span className="h-1.5 w-1.5 rounded-full bg-current" />
              {item.status.replaceAll('_', ' ')}
            </span>
          </div>
          <h1 className="mt-4 text-[26px] font-bold leading-tight tracking-tight text-[var(--text-primary)] sm:text-4xl">{item.title}</h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-[var(--text-secondary)]">{item.summary}</p>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <a href={item.registrationUrl} target="_blank" rel="noreferrer" className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2">
              Open registration
              <External />
            </a>
            {item.informationUrl ? (
              <a href={item.informationUrl} target="_blank" rel="noreferrer" className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-5 py-3 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[var(--background)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]">
                Official details
                <External />
              </a>
            ) : null}
          </div>
        </div>

        <div className="grid gap-8 p-5 sm:p-8 md:grid-cols-[1.5fr_1fr]">
          <div className="space-y-8">
            <section className="rise" style={stagger(1)}>
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">About this opportunity</h2>
              <p className="mt-2 whitespace-pre-line text-sm leading-7 text-[var(--text-secondary)]">{item.description || item.summary}</p>
            </section>

            <section className="rise" style={stagger(2)}>
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">Skills and focus areas</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {item.skills.length ? item.skills.map((skill) => <span key={skill} className="rounded-full border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--text-secondary)]">{skill}</span>) : <p className="text-sm text-[var(--text-secondary)]">No specific skills were provided.</p>}
              </div>
            </section>

            <section className="rise" style={stagger(3)}>
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">Eligibility</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.eligibility.summary}</p>
              {item.eligibility.status ? (
                <p className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-[var(--primary-soft)] px-3 py-1 text-xs font-semibold text-[var(--primary)]">
                  <span className="h-1.5 w-1.5 rounded-full bg-current" />
                  Status: {item.eligibility.status.replaceAll('_', ' ')}
                </p>
              ) : null}
              {item.eligibility.statusReason ? <p className="mt-2 text-sm text-[var(--text-secondary)]">{item.eligibility.statusReason}</p> : null}
              {item.eligibility.requirements?.length ? (
                <ul className="mt-4 space-y-2.5">
                  {item.eligibility.requirements.map((requirement) => (
                    <li key={requirement} className="flex gap-3 text-sm leading-6 text-[var(--text-secondary)]">
                      <span aria-hidden="true" className="mt-[11px] h-0.5 w-3 shrink-0 rounded-full bg-[var(--primary)]" />
                      {requirement}
                    </li>
                  ))}
                </ul>
              ) : null}
            </section>
          </div>

          <aside className="rise h-fit rounded-3xl border border-[var(--border)] p-5 max-md:order-first md:sticky md:top-6" style={stagger(1)}>
            <h2 className="font-semibold text-[var(--text-primary)]">At a glance</h2>

            <div className="mt-4 rounded-2xl bg-[var(--surface-alt)] p-4">
              <p className="text-xs text-[var(--text-muted)]">Registration deadline</p>
              <p className="mt-1 text-sm font-semibold leading-snug text-[var(--text-primary)]">{formatDate(item.deadlineAt)}</p>
              {deadline && (
                <span className="mt-2.5 inline-block rounded-full px-2.5 py-1 text-xs font-semibold" style={{ backgroundColor: deadline.bg, color: deadline.fg }}>
                  {deadline.text}
                </span>
              )}
            </div>

            <dl className="mt-5 space-y-4 text-sm">
              {glance.map(([label, value]) => (
                <div key={label}>
                  <dt className="text-[var(--text-muted)]">{label}</dt>
                  <dd className="mt-1 font-medium text-[var(--text-primary)]">{value}</dd>
                </div>
              ))}
            </dl>

            {item.organizer.websiteUrl ? (
              <a href={item.organizer.websiteUrl} target="_blank" rel="noreferrer" className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-[var(--primary)] hover:underline">
                Organizer website
                <External />
              </a>
            ) : null}
          </aside>
        </div>
      </article>

      <p className="mt-4 text-xs leading-5 text-[var(--text-muted)]">Registration and eligibility information is provided by the competition source. Verify the latest rules on the official page before registering.</p>
    </main>
  );
}