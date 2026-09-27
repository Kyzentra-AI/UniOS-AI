'use client';

import type { Mission } from '@/types/mission';

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
  const isCompleted = mission.status === 'COMPLETED';
  const isInProgress = mission.status === 'IN_PROGRESS';
  const isPending = mission.status === 'PENDING';
  const isDeferred = mission.status === 'DEFERRED';
  const isSkipped = mission.status === 'SKIPPED';

  const isBusy =
    isStarting ||
    isCompleting ||
    isDeferring ||
    isSkipping;

  return (
    <article
      className="rounded-2xl border p-5"
      style={{
        background: 'var(--surface)',
        borderColor: 'var(--border)',
      }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 gap-3">
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-semibold"
            style={{
              background: 'var(--primary-soft)',
              color: 'var(--primary)',
            }}
          >
            {mission.sequence ?? '—'}
          </div>

          <div className="min-w-0">
            <p
              className="text-xs font-medium uppercase tracking-wide"
              style={{
                color: 'var(--text-muted)',
              }}
            >
              Mission
            </p>

            <h3
              className="mt-1 text-base font-semibold"
              style={{
                color: 'var(--text-primary)',
              }}
            >
              {mission.title}
            </h3>
          </div>
        </div>

        <span
          className="shrink-0 rounded-full px-3 py-1 text-xs font-medium"
          style={{
            background: isCompleted
              ? 'var(--primary-soft)'
              : isInProgress
                ? 'var(--feature-blue-soft)'
                : 'var(--surface-alt)',
            color: isCompleted
              ? 'var(--primary)'
              : isInProgress
                ? 'var(--feature-blue)'
                : 'var(--text-secondary)',
          }}
        >
          {mission.status.replaceAll('_', ' ')}
        </span>
      </div>

      {mission.description && (
        <p
          className="mt-4 text-sm leading-6"
          style={{
            color: 'var(--text-secondary)',
          }}
        >
          {mission.description}
        </p>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        {mission.mission_type && (
          <span
            className="rounded-lg px-2.5 py-1 text-xs"
            style={{
              background: 'var(--surface-alt)',
              color: 'var(--text-secondary)',
            }}
          >
            {mission.mission_type}
          </span>
        )}

        {mission.subject && (
          <span
            className="rounded-lg px-2.5 py-1 text-xs"
            style={{
              background: 'var(--surface-alt)',
              color: 'var(--text-secondary)',
            }}
          >
            {mission.subject}
          </span>
        )}

        {mission.estimated_minutes != null && (
          <span
            className="rounded-lg px-2.5 py-1 text-xs"
            style={{
              background: 'var(--surface-alt)',
              color: 'var(--text-secondary)',
            }}
          >
            {mission.estimated_minutes} min
          </span>
        )}
      </div>

      <div
        className="mt-5 flex items-center justify-between gap-4 border-t pt-4"
        style={{
          borderColor: 'var(--border)',
        }}
      >
        <span
          className="text-xs"
          style={{
            color: 'var(--text-muted)',
          }}
        >
          {isCompleted
            ? 'Mission completed'
            : isInProgress
              ? 'Currently in progress'
              : isDeferred
                ? 'Mission deferred'
                : isSkipped
                  ? 'Mission skipped'
                  : 'Ready to start'}
        </span>

        <div className="flex items-center gap-2">
          {isPending || isDeferred ? (
            <button
              type="button"
              onClick={onStart}
              disabled={isBusy || !onStart}
              className="rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50"
              style={{
                background: 'var(--primary)',
                color: 'var(--surface)',
              }}
            >
              {isStarting ? 'Starting...' : 'Start Mission'}
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
                    borderColor: 'var(--border)',
                    color: 'var(--text-secondary)',
                  }}
                >
                  {isDeferring ? 'Deferring...' : 'Defer'}
                </button>
              )}

              {onSkip && (
                <button
                  type="button"
                  onClick={onSkip}
                  disabled={isBusy}
                  className="rounded-xl border px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50"
                  style={{
                    borderColor: 'var(--border)',
                    color: 'var(--text-secondary)',
                  }}
                >
                  {isSkipping ? 'Skipping...' : 'Skip'}
                </button>
              )}

              <button
                type="button"
                onClick={onComplete}
                disabled={isBusy || !onComplete}
                className="rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50"
                style={{
                  background: 'var(--primary)',
                  color: 'var(--surface)',
                }}
              >
                {isCompleting
                  ? 'Completing...'
                  : 'Complete Mission'}
              </button>
            </>
          ) : null}
        </div>
      </div>
    </article>
  );
}