'use client';

import type { ReactNode } from 'react';

export function BuildLoading({ label = 'Loading your workspace…' }: { label?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="rise rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-8"
    >
      <div className="flex items-center gap-3 text-sm text-[var(--muted-foreground)]">
        <span className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
        {label}
      </div>

      <div className="mt-6 space-y-3" aria-hidden="true">
        <div className="skeleton h-5 w-2/5 rounded-md" />
        <div className="skeleton h-4 w-4/5 rounded-md" />
        <div className="skeleton h-4 w-3/5 rounded-md" />
        <div className="skeleton h-16 w-full rounded-2xl" />
      </div>
    </div>
  );
}

export function BuildEmpty({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="rise rounded-3xl border border-dashed border-[var(--border)] bg-[var(--surface)] px-6 py-10 text-center sm:py-12">
      <h3 className="text-base font-semibold text-[var(--foreground)]">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--muted-foreground)]">
        {description}
      </p>
      {action ? <div className="mt-6 flex justify-center">{action}</div> : null}
    </div>
  );
}

export function BuildError({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="rise rounded-3xl border border-red-500/30 bg-red-500/5 p-5"
    >
      <div className="flex items-center gap-2.5">
        <span className="h-2 w-2 shrink-0 rounded-full bg-red-500" />
        <p className="font-semibold text-[var(--foreground)]">Something went wrong</p>
      </div>

      <p className="mt-1.5 break-words pl-[18px] text-sm leading-6 text-[var(--muted-foreground)]">
        {message}
      </p>

      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="ml-[18px] mt-4 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm font-medium text-[var(--foreground)] transition hover:bg-[var(--surface-hover)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
        >
          Try again
        </button>
      ) : null}
    </div>
  );
}