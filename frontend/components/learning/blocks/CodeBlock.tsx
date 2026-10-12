import type { LessonBlock } from '@/types/learning';

interface CodeBlockProps {
  block: LessonBlock;
}

export default function CodeBlock({
  block,
}: CodeBlockProps) {
  return (
    <section className="space-y-3">
      {block.title && (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--primary)]">
        {block.language && (
          <div className="border-b border-white/10 px-4 py-2 text-xs text-white/70">
            {block.language}
          </div>
        )}

        <pre className="overflow-x-auto p-5 text-sm leading-6 text-white">
          <code>{block.code ?? block.content}</code>
        </pre>
      </div>
    </section>
  );
}