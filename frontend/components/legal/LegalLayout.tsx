
import type { ReactNode } from 'react';
import Link from 'next/link';

interface LegalLayoutProps {
  title: string;
  subtitle: string;
  lastUpdated?: string;
  children: ReactNode;
}

export default function LegalLayout({
  title,
  subtitle,
  lastUpdated,
  children,
}: LegalLayoutProps) {
  return (
    <main className="min-h-screen bg-[var(--background)] px-4 py-14 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl">

        <div className="mb-10">
          <Link
            href="/"
            className="mb-8 inline-flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)] transition hover:text-[var(--primary)]"
          >
            ← Back to UniOS.ai
          </Link>

          <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-[var(--primary)]">
            UniOS.ai
          </p>

          <h1 className="text-4xl font-bold tracking-tight text-[var(--text-primary)] sm:text-5xl">
            {title}
          </h1>

          <p className="mt-4 max-w-2xl text-base leading-relaxed text-[var(--text-secondary)]">
            {subtitle}
          </p>

          {lastUpdated && (
            <p className="mt-5 text-sm text-[var(--text-muted)]">
              Effective / Last Updated: {lastUpdated}
            </p>
          )}
        </div>

        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-10">
          <div className="legal-content space-y-9 text-sm leading-7 text-[var(--text-secondary)]">
            {children}
          </div>
        </div>

        <div className="mt-8 flex flex-wrap gap-5 border-t border-[var(--border)] pt-6 text-sm text-[var(--text-secondary)]">
          <Link href="/about" className="hover:text-[var(--primary)]">
            About Us
          </Link>
          <Link href="/privacy" className="hover:text-[var(--primary)]">
            Privacy Policy
          </Link>
          <Link href="/terms" className="hover:text-[var(--primary)]">
            Terms of Service
          </Link>
        </div>

      </div>
    </main>
  );
}
