export default function Loading() {
  return (
    <div className="flex min-h-[300px] items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)]">
      <div className="text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />

        <p className="mt-4 text-sm font-medium text-[var(--text-primary)]">
          Loading lesson...
        </p>

        <p className="mt-1 text-sm text-[var(--text-muted)]">
          Preparing your learning workspace.
        </p>
      </div>
    </div>
  );
}