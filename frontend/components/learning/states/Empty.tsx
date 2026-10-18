interface LearningEmptyProps {
  message?: string;
}

export default function Empty({
  message = 'No learning content is available yet.',
}: LearningEmptyProps) {
  return (
    <div className="flex min-h-[300px] items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)]">
      <div className="max-w-md text-center">
        <p className="text-base font-semibold text-[var(--text-primary)]">
          Nothing to learn here yet
        </p>

        <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
          {message}
        </p>
      </div>
    </div>
  );
}