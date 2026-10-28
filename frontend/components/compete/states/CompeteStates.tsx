'use client';

import type { ReactNode } from 'react';
import { stagger } from '@/components/roadmap/UI';

export function CompeteLoadingState({
  label = 'Loading competitions…',
  variant = 'panel',
}: {
  label?: string;
  variant?: 'panel' | 'grid';
}) {
  if (variant === 'grid') {
    return (
      <div role="status" aria-live="polite">
        <span className="sr-only">{label}</span>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3" aria-hidden="true">
          {[0, 1, 2, 3, 4, 5].map((n) => (
            <div
              key={n}
              className="rise rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5"
              style={stagger(n)}
            >
              <div className="flex gap-2">
                <div className="skeleton h-6 w-24 rounded-full" />
                <div className="skeleton h-6 w-16 rounded-full" />
              </div>
              <div className="skeleton mt-5 h-5 w-4/5 rounded-md" />
              <div className="skeleton mt-3 h-4 w-full rounded-md" />
              <div className="skeleton mt-2 h-4 w-3/4 rounded-md" />
              <div className="mt-6 space-y-2.5">
                <div className="skeleton h-4 w-2/3 rounded-md" />
                <div className="skeleton h-4 w-1/2 rounded-md" />
              </div>
              <div className="skeleton mt-6 h-10 w-32 rounded-xl" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className="rise rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-8"
    >
      <div className="flex items-center gap-3 text-sm text-[var(--text-secondary)]">
        <span className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
        {label}
      </div>
      <div className="mt-6 space-y-3" aria-hidden="true">
        <div className="skeleton h-6 w-1/2 rounded-md" />
        <div className="skeleton h-4 w-4/5 rounded-md" />
        <div className="skeleton h-4 w-3/5 rounded-md" />
        <div className="skeleton h-24 w-full rounded-2xl" />
      </div>
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
    <div className="rise rounded-3xl border border-dashed border-[var(--border)] bg-[var(--surface)] px-6 py-12 text-center">
      <div
        aria-hidden="true"
        className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full border-2 border-dashed border-[var(--primary)] bg-[var(--primary-soft)]"
      >
        <span className="h-2.5 w-2.5 rounded-full bg-[var(--primary)]" />
      </div>
      <h3 className="font-semibold text-[var(--text-primary)]">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--text-secondary)]">{description}</p>
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
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
    <div role="alert" className="rise rounded-3xl border border-[var(--danger-border)] bg-[var(--danger-soft)] p-5 sm:p-6">
      <div className="flex items-center gap-2.5">
        <span className="h-2 w-2 shrink-0 rounded-full bg-[var(--danger-text)]" />
        <h3 className="font-semibold text-[var(--danger-text)]">We couldn’t load competitions</h3>
      </div>
      <p className="mt-2 break-words pl-[18px] text-sm leading-6 text-[var(--danger-text)]">
        {message || 'Something went wrong while requesting competition data.'}
      </p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="ml-[18px] mt-4 rounded-xl border border-[var(--danger-border)] px-4 py-2 text-sm font-medium text-[var(--danger-text)] transition hover:opacity-80 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--danger-text)]"
        >
          Try again
        </button>
      ) : null}
    </div>
  );
}