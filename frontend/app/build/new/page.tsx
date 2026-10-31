'use client';

import Link from 'next/link';

import BuildProjects from '@/components/build/projects/BuildProjects';
import { Chevron } from '@/components/roadmap/UI';

export default function NewBuildProjectPage() {
  return (
    <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
      <div className="rise mb-6">
        <Link
          href="/build"
          className="group inline-flex items-center gap-1 rounded-md py-1 text-sm font-medium text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
        >
          <Chevron className="rotate-180 transition-transform duration-200 group-hover:-translate-x-0.5" />
          Back to Build
        </Link>

        <h1 className="mt-4 text-[28px] font-semibold leading-tight tracking-tight text-[var(--foreground)] sm:text-3xl">
          Create a project
        </h1>

        <p className="mt-2 max-w-2xl text-[15px] leading-6 text-[var(--muted-foreground)]">
          Define your project, set its goal, and choose the skills you want to
          develop.
        </p>
      </div>

      <BuildProjects />
    </main>
  );
}