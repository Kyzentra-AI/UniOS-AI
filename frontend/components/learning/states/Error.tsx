interface LearningErrorProps {
  message?: string;
  onRetry?: () => void;
}

export default function Error({
  message = 'We could not load the learning content.',
  onRetry,
}: LearningErrorProps) {
  return (
    <div className="flex min-h-[300px] items-center justify-center rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)]">
      <div className="max-w-md text-center">
        <p className="text-base font-semibold text-[var(--danger-text)]">
          Something went wrong
        </p>

        <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
          {message}
        </p>

        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-5 rounded-md bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white transition hover:bg-[var(--primary-hover)]"
          >
            Try again
          </button>
        )}
      </div>
    </div>
  );
}