'use client';

import Link from 'next/link';
import { useCompetition } from '@/hooks/useCompete';
import { CompeteEmptyState, CompeteErrorState, CompeteLoadingState } from '@/components/compete/states/CompeteStates';

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

export default function CompetitionDetails({ competitionId }: { competitionId: string }) {
  const query = useCompetition(competitionId);

  if (query.isPending) return <main className="mx-auto max-w-5xl px-4 py-8"><CompeteLoadingState label="Loading competition details…" /></main>;
  if (query.isError) return <main className="mx-auto max-w-5xl px-4 py-8"><CompeteErrorState message={query.error instanceof Error ? query.error.message : undefined} onRetry={() => void query.refetch()} /></main>;
  if (!query.data?.competition) return <main className="mx-auto max-w-5xl px-4 py-8"><CompeteEmptyState title="Competition not found" description="This opportunity may have expired or been removed." /></main>;

  const item = query.data.competition;

  return (
    <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <Link href="/compete" className="text-sm font-semibold text-[var(--primary)] hover:underline">← Back to Compete</Link>
      <article className="mt-5 overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)]">
        <div className="border-b border-[var(--border)] bg-[var(--surface-alt)] p-6 sm:p-8">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-[var(--primary-soft)] px-3 py-1 text-xs font-semibold text-[var(--primary)]">{item.type.replaceAll('_', ' ')}</span>
            <span className="rounded-full border border-[var(--border)] px-3 py-1 text-xs text-[var(--text-secondary)]">{item.status.replaceAll('_', ' ')}</span>
          </div>
          <h1 className="mt-4 text-3xl font-bold tracking-tight text-[var(--text-primary)]">{item.title}</h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-[var(--text-secondary)]">{item.summary}</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <a href={item.registrationUrl} target="_blank" rel="noreferrer" className="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-white hover:bg-[var(--primary-hover)]">Open registration ↗</a>
            {item.informationUrl ? <a href={item.informationUrl} target="_blank" rel="noreferrer" className="rounded-xl border border-[var(--border)] px-5 py-3 text-sm font-semibold text-[var(--text-primary)] hover:bg-[var(--background)]">Official details ↗</a> : null}
          </div>
        </div>

        <div className="grid gap-8 p-6 sm:p-8 md:grid-cols-[1.5fr_1fr]">
          <div className="space-y-7">
            <section>
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">About this opportunity</h2>
              <p className="mt-2 whitespace-pre-line text-sm leading-7 text-[var(--text-secondary)]">{item.description || item.summary}</p>
            </section>
            <section>
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">Skills and focus areas</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {item.skills.length ? item.skills.map((skill) => <span key={skill} className="rounded-full border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--text-secondary)]">{skill}</span>) : <p className="text-sm text-[var(--text-secondary)]">No specific skills were provided.</p>}
              </div>
            </section>
            <section>
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">Eligibility</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.eligibility.summary}</p>
              {item.eligibility.status ? <p className="mt-3 inline-flex rounded-full bg-[var(--primary-soft)] px-3 py-1 text-xs font-semibold text-[var(--primary)]">Status: {item.eligibility.status.replaceAll('_', ' ')}</p> : null}
              {item.eligibility.statusReason ? <p className="mt-2 text-sm text-[var(--text-secondary)]">{item.eligibility.statusReason}</p> : null}
              {item.eligibility.requirements?.length ? <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">{item.eligibility.requirements.map((requirement) => <li key={requirement}>{requirement}</li>)}</ul> : null}
            </section>
          </div>

          <aside className="h-fit rounded-2xl border border-[var(--border)] p-5">
            <h2 className="font-semibold text-[var(--text-primary)]">At a glance</h2>
            <dl className="mt-4 space-y-4 text-sm">
              <div><dt className="text-[var(--text-muted)]">Organizer</dt><dd className="mt-1 font-medium text-[var(--text-primary)]">{item.organizer.name}</dd></div>
              <div><dt className="text-[var(--text-muted)]">Registration deadline</dt><dd className="mt-1 font-medium text-[var(--text-primary)]">{formatDate(item.deadlineAt)}</dd></div>
              <div><dt className="text-[var(--text-muted)]">Starts</dt><dd className="mt-1 font-medium text-[var(--text-primary)]">{formatDate(item.startsAt)}</dd></div>
              <div><dt className="text-[var(--text-muted)]">Ends</dt><dd className="mt-1 font-medium text-[var(--text-primary)]">{formatDate(item.endsAt)}</dd></div>
              <div><dt className="text-[var(--text-muted)]">Difficulty</dt><dd className="mt-1 font-medium text-[var(--text-primary)]">{item.difficulty.replaceAll('_', ' ')}</dd></div>
              <div><dt className="text-[var(--text-muted)]">Goal</dt><dd className="mt-1 font-medium text-[var(--text-primary)]">{item.goals.map((goal) => goal.replaceAll('_', ' ')).join(', ') || 'Not specified'}</dd></div>
              {item.prizeSummary ? <div><dt className="text-[var(--text-muted)]">Prize / benefits</dt><dd className="mt-1 font-medium text-[var(--text-primary)]">{item.prizeSummary}</dd></div> : null}
              <div><dt className="text-[var(--text-muted)]">Team size</dt><dd className="mt-1 font-medium text-[var(--text-primary)]">{item.eligibility.minimumTeamSize ?? '—'}–{item.eligibility.maximumTeamSize ?? '—'} participants</dd></div>
            </dl>
            {item.organizer.websiteUrl ? <a href={item.organizer.websiteUrl} target="_blank" rel="noreferrer" className="mt-5 inline-block text-sm font-semibold text-[var(--primary)] hover:underline">Organizer website ↗</a> : null}
          </aside>
        </div>
      </article>
      <p className="mt-4 text-xs leading-5 text-[var(--text-muted)]">Registration and eligibility information is provided by the competition source. Verify the latest rules on the official page before registering.</p>
    </main>
  );
}
