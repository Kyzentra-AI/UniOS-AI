import type { LessonBlock } from '@/types/learning';

interface DiagramBlockProps {
  block: LessonBlock;
}

export default function DiagramBlock({
  block,
}: DiagramBlockProps) {
  return (
    <section className="space-y-3">
      {block.title && (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      {block.url ? (
        <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface)]">
          <img
            src={block.url}
            alt={
              block.caption ??
              block.title ??
              'Lesson diagram'
            }
            className="max-h-[500px] w-full object-contain"
          />
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-alt)] p-8 text-center text-sm text-[var(--text-muted)]">
          Diagram content will appear here.
        </div>
      )}
    </section>
  );
}