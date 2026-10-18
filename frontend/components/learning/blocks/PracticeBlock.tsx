import type { LessonBlock } from '@/types/learning';

interface PracticeBlockProps {
  block: LessonBlock;
}

export default function PracticeBlock({
  block,
}: PracticeBlockProps) {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--feature-blue-soft)] p-5">
      {block.title && (
        <h3 className="mb-2 text-base font-semibold text-[var(--feature-blue)]">
          {block.title}
        </h3>
      )}

      {block.content && (
        <p className="whitespace-pre-line text-sm leading-7 text-[var(--text-primary)]">
          {block.content}
        </p>
      )}
    </section>
  );
}