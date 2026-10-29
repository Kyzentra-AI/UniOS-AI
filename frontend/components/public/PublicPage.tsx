
import Link from 'next/link';

interface PublicPageProps {
  eyebrow: string;
  title: string;
  description: string;
  sections?: {
    title: string;
    description: string;
  }[];
}

export default function PublicPage({
  eyebrow,
  title,
  description,
  sections = [],
}: PublicPageProps) {
  return (
    <main className="min-h-[calc(100vh-4rem)] bg-[var(--background)] text-[var(--foreground)]">
      <section className="mx-auto max-w-6xl px-5 py-20 sm:px-8 sm:py-28">
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-[var(--primary)]">
          {eyebrow}
        </p>

        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl">
          {title}
        </h1>

        <p className="mt-6 max-w-2xl text-base leading-7 text-[var(--text-secondary)] sm:text-lg">
          {description}
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/register"
            className="rounded-lg bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-[var(--surface)] transition hover:bg-[var(--primary-hover)]"
          >
            Get Started
          </Link>

          <Link
            href="/login"
            className="rounded-lg border border-[var(--border)] px-5 py-3 text-sm font-semibold transition hover:bg-[var(--primary-soft)]"
          >
            Log In
          </Link>
        </div>

        {sections.length > 0 && (
          <div className="mt-16 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {sections.map((section) => (
              <article
                key={section.title}
                className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6"
              >
                <h2 className="text-lg font-semibold">{section.title}</h2>
                <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
                  {section.description}
                </p>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
