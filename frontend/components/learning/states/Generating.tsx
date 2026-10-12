export default function Generating() {
  return (
    <div className="flex min-h-[300px] items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)]">
      <div className="max-w-md text-center">
        <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-[var(--primary-soft)]">
          <span className="text-lg text-[var(--primary)]">✦</span>
        </div>

        <p className="mt-4 text-sm font-semibold text-[var(--text-primary)]">
          Generating your lesson...
        </p>

        <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
          Your learning content is being prepared based on your current
          learning context.
        </p>
      </div>
    </div>
  );
}