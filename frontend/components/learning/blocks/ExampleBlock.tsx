import type { LessonBlock } from '@/types/learning';

interface ExampleBlockProps {
  block: LessonBlock;
}

export default function ExampleBlock({
  block,
}: ExampleBlockProps) {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--feature-purple-soft)] p-5">
      {block.title && (
        <h3 className="mb-2 text-base font-semibold text-[var(--feature-purple)]">
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