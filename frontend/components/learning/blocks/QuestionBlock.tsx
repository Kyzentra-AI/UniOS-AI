'use client';

import { useState } from 'react';

import type { LessonBlock } from '@/types/learning';

interface QuestionBlockProps {
  block: LessonBlock;
}

export default function QuestionBlock({
  block,
}: QuestionBlockProps) {
  const [selectedOption, setSelectedOption] =
    useState<string | null>(null);

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
      {block.title && (
        <h3 className="mb-3 text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      {block.content && (
        <p className="mb-5 text-sm leading-6 text-[var(--text-secondary)]">
          {block.content}
        </p>
      )}

      {block.options && block.options.length > 0 && (
        <div className="space-y-2">
          {block.options.map((option) => {
            const isSelected = selectedOption === option;

            return (
              <button
                key={option}
                type="button"
                onClick={() => setSelectedOption(option)}
                className={`w-full rounded-lg border px-4 py-3 text-left text-sm transition ${
                  isSelected
                    ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                    : 'border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)] hover:bg-[var(--surface-alt)]'
                }`}
              >
                {option}
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}