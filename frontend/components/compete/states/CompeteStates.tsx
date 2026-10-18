'use client';

import type { ReactNode } from 'react';

export function CompeteLoadingState({ label = 'Loading competitions…' }: { label?: string }) {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center">
      <div className="mx-auto mb-3 h-7 w-7 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
      <p className="text-sm text-[var(--text-secondary)]">{label}</p>
    </div>
  );
}

export function CompeteEmptyState({
  title = 'No competitions found',
  description = 'Try changing your search or filters.',
  action,
}: {
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface)] px-6 py-12 text-center">
      <div className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-[var(--primary-soft)] text-lg text-[var(--primary)]">
        ✦
      </div>
      <h3 className="font-semibold text-[var(--text-primary)]">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm text-[var(--text-secondary)]">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

export function CompeteErrorState({
  message,
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div role="alert" className="rounded-2xl border border-[var(--danger-border)] bg-[var(--danger-soft)] p-6">
      <h3 className="font-semibold text-[var(--danger-text)]">We couldn’t load competitions</h3>
      <p className="mt-2 text-sm text-[var(--danger-text)]">
        {message || 'Something went wrong while requesting competition data.'}
      </p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-lg border border-[var(--danger-border)] px-4 py-2 text-sm font-medium text-[var(--danger-text)] hover:opacity-80"
        >
          Try again
        </button>
      ) : null}
    </div>
  );
}
