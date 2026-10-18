interface LearningOfflineProps {
  onRetry?: () => void;
}

export default function Offline({
  onRetry,
}: LearningOfflineProps) {
  return (
    <div className="flex min-h-[300px] items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)]">
      <div className="max-w-md text-center">
        <p className="text-base font-semibold text-[var(--text-primary)]">
          Connection interrupted
        </p>

        <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
          Your connection appears to be unavailable. Check your network
          and try again.
        </p>

        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-5 rounded-md border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)]"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}