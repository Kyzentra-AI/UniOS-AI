import type { LessonBlock } from '@/types/learning';

interface TextBlockProps {
  block: LessonBlock;
}

export default function TextBlock({
  block,
}: TextBlockProps) {
  return (
    <section className="space-y-2">
      {block.title && (
        <h3 className="text-lg font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      {block.content && (
        <p className="whitespace-pre-line text-sm leading-7 text-[var(--text-secondary)]">
          {block.content}
        </p>
      )}
    </section>
  );
}